import os
import math
import time
import json
import yaml
import arrow
import numpy
import base64
import pandas
import fuzzyset
import pendulum
import itertools
import subprocess
import collections
from Bio import SeqIO
from time import sleep
from O365 import Account
from django.db.models import Q
from celery import shared_task
from dotenv import load_dotenv
from django.conf import settings
from django.utils import timezone
from zipfile import ZipFile, ZIP_DEFLATED
from sequences.models import Download_Handler, Metadata_Handler, Frontend_Handler

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

@shared_task(bind=True)
def create_config_file(self, upload_info):
	upload_date = pendulum.now('Asia/Kolkata').format('YYYY-MM-DD_hh-mm-ss-A')
	config_data = {
		"analysis_time": upload_date,
		"base_path": settings.MEDIA_ROOT,
		"uploaded_by": upload_info['username'],
		"sequences_uploaded": upload_info['uploaded'],
	}
	configfile_loc = os.path.join(settings.BASE_DIR, 'workflow', 'config', f"config_{upload_date}.yaml")
	yaml.dump(config_data, open(configfile_loc, 'w'))
	snakefile_loc = os.path.join(settings.BASE_DIR, 'workflow', 'Snakefile')
	command = f"exec snakemake --snakefile {snakefile_loc} --configfile {configfile_loc} --cores 20"
	snakemake_command = subprocess.run(command, shell = True)
	return 'Pipeline run completed'

def get_my_metadata(user_obj):
	temp = []
	metadata_qs = Metadata_Handler.objects.filter(Q(user=user_obj))
	for index,i in enumerate(metadata_qs):
		temp.append(i.metadata)
	return_dict = list(itertools.chain(*temp))
	return return_dict

def get_dashboard(user_obj):
	frontend_obj = Frontend_Handler.objects.last()
	dashboard = {
		"genomes_sequenced": int(frontend_obj.genomes_sequenced),
		"variants_catalogued": int(frontend_obj.variants_catalogued),
		"lineages_catalogued": int(frontend_obj.lineages_catalogued),
		"states_covered": int(frontend_obj.states_covered),
	}
	return dashboard

def get_all_metadata(each_page, page):
	frontend_obj = Frontend_Handler.objects.last()
	start = 0 + (each_page * (page - 1))
	end = (each_page - 1) + (each_page * (page -1))
	required_metadata = frontend_obj.metadata[start:(end+1)]
	data = {
		"metadata": required_metadata,
		"total_length": math.ceil(len(frontend_obj.metadata)/each_page)
	}
	return data

def get_map_data(user_obj):
	frontend_obj = Frontend_Handler.objects.last()
	return frontend_obj.map_data

def get_bar_chart_data(user_obj):
	frontend_obj = Frontend_Handler.objects.last()
	return frontend_obj.bar_chart_data

def get_treemap_chart_data(user_obj):
	frontend_obj = Frontend_Handler.objects.last()
	return frontend_obj.treemap_chart_data

def get_lineage_definition_data(user_obj):
	frontend_obj = Frontend_Handler.objects.last()
	return frontend_obj.lineage_definition_data

def create_download_link(workflow_info):
	download_link = f"{os.getenv('DOWNLOAD_URL')}/INSACOG_data_{workflow_info['upload_time']}.zip"
	download_obj = Download_Handler(download_link = download_link)
	download_obj.save()

@shared_task(bind=True)
def create_frontend_entry(self, workflow_info):
	workflow_df = pandas.DataFrame(workflow_info["message"])
	workflow_df['Collection date'] = pandas.to_datetime(workflow_df['Collection date'], format="%Y-%m-%d")
	month_values = sorted(workflow_df['Collection date'])
	month_keys = [i.strftime('%b-%Y') for i in month_values]
	workflow_df['Collection month'] = month_keys
	month_keys = pandas.DataFrame(month_keys)[0].unique().tolist()

	genomes_sequenced = len(workflow_df)
	all_variants = []
	for i in workflow_df.index:
		if(isinstance(workflow_df.iloc[i]['aaSubstitutions'], str)):
			all_variants.append(workflow_df.iloc[i]['aaSubstitutions'].split(','))
		if(isinstance(workflow_df.iloc[i]['aaDeletions'], str)):
			all_variants.append(workflow_df.iloc[i]['aaDeletions'].split(','))
	all_variants = list(itertools.chain(*all_variants))
	unique_variants = pandas.unique(all_variants).tolist()
	variants_catalogued = len(unique_variants)
	lineages_catalogued = len(pandas.unique(workflow_df['lineage']))
	states_covered = len(pandas.unique(workflow_df['State']))

	map_data = []
	bar_chart_data = {}
	treemap_chart_data = {}
	lineage_definition_data = {}
	genes = ['E', 'M', 'N', 'ORF1a', 'ORF1b', 'ORF3a', 'ORF6', 'ORF7a', 'ORF7b', 'ORF8', 'ORF9b', 'S']
	treemap_chart_data['genes'] = genes

	for (key,value) in dict(collections.Counter(workflow_df['District'].tolist())).items():
		map_data.append({
			"name": key,
			"value": value
		})

	bar_chart_data['xAxis'] = {
		"month": month_keys
	}
	bar_chart_data['India'] = {}
	for i in pandas.unique(workflow_df['lineage']).tolist():
		lineage_metadata = workflow_df.iloc[workflow_df.index[workflow_df['lineage'].isin([i])].tolist()]
		lineage_count = len(lineage_metadata)
		temp = []
		for j in lineage_metadata['aaSubstitutions']:
			if(isinstance(j, str)):
				temp.append(j.split(','))
		aaSubstitution = list(itertools.chain(*temp))
		lineage_definition_data[i] = [key for index,key in enumerate(aaSubstitution) if(index<20)]
		bar_chart_data['India'][i] = {}
		bar_chart_data['India'][i]['name'] = i
		lineage_month = dict(collections.Counter(lineage_metadata['Collection month']))
		for j in month_keys:
			if(not j in list(lineage_month.keys())):
				lineage_month[j] = 0
		bar_chart_data['India'][i]['month'] = [lineage_month[i] for i in month_keys]

	treemap_chart_data['India'] = {}
	temp = []
	for i in workflow_df['aaSubstitutions']:
		if(isinstance(i, str)):
			temp.append(i.split(','))
	aaSubstitution = list(itertools.chain(*temp))

	for i in genes:
		gene_aaSubstitution = []
		treemap_chart_data['India'][i] = {}
		for j in aaSubstitution:
			if(j.startswith(f'{i}')):
				gene_aaSubstitution.append(j)
		gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
		treemap_chart_data['India'][i]['name'] = i
		treemap_chart_data['India'][i]['children'] = []
		for index,value in gene_subsitution_counter.items():
			treemap_chart_data['India'][i]['children'].append({
				"name": index,
				"value": value
			})

	for i in pandas.unique(workflow_df['State']).tolist():
		state_metadata = workflow_df.iloc[workflow_df.index[workflow_df['State'].isin([i])].tolist()]
		state_metadata.reset_index(drop = True, inplace = True)
		treemap_chart_data[i] = {}
		temp = []
		for j in state_metadata['aaSubstitutions']:
			if(isinstance(j, str)):
				temp.append(j.split(','))
		aaSubstitution = list(itertools.chain(*temp))
		for j in genes:
			gene_aaSubstitution = []
			treemap_chart_data[i][j] = {}
			for k in aaSubstitution:
				if(k.startswith(f'{j}')):
					gene_aaSubstitution.append(k)
			gene_subsitution_counter = dict(collections.Counter(gene_aaSubstitution))
			treemap_chart_data[i][j]['name'] = j
			treemap_chart_data[i][j]['children'] = []
			for index,value in gene_subsitution_counter.items():
				treemap_chart_data[i][j]['children'].append({
					"name": index,
					"value": value
				})

	for i in pandas.unique(workflow_df['State']).tolist():
		state_metadata = workflow_df.iloc[workflow_df.index[workflow_df['State'].isin([i])].tolist()]
		state_metadata.reset_index(drop = True, inplace = True)
		bar_chart_data[i] = {}
		for j in pandas.unique(state_metadata['lineage']).tolist():
			lineage_metadata = state_metadata.iloc[state_metadata.index[state_metadata['lineage'].isin([j])].tolist()]
			bar_chart_data[i][j] = {}
			bar_chart_data[i][j]['name'] = j
			lineage_month = dict(collections.Counter(lineage_metadata['Collection month']))
			for k in month_keys:
				if(not k in list(lineage_month.keys())):
					lineage_month[k] = 0
			bar_chart_data[i][j]['month'] = [lineage_month[month] for month in month_keys]

	download_obj = Frontend_Handler(
		map_data = map_data,
		bar_chart_data = bar_chart_data,
		states_covered = states_covered,
		unique_variants = unique_variants,
		metadata = workflow_info["message"],
		genomes_sequenced = genomes_sequenced,
		treemap_chart_data = treemap_chart_data,
		variants_catalogued = variants_catalogued,
		lineages_catalogued = lineages_catalogued,
		lineage_definition_data = lineage_definition_data,
	)
	download_obj.save()

def send_email_upload(user_info):
	credentials = (os.getenv('ONEDRIVE_CLIENT'), os.getenv('ONEDRIVE_SECRET'))
	account = Account(credentials, auth_flow_type='authorization')
	if(account.is_authenticated):
		message = account.new_message()
		# message.to.add(['aks1@nibmg.ac.in', 'nkb1@nibmg.ac.in', 'ap3@nibmg.ac.in', 'rezwanuzzaman.laskar@gmail.com'])
		message.to.add(['aks1@nibmg.ac.in'])
		message.subject = '✅|📤 Upload Info [ INSACOG DataHub ]'
		html_content	= f"""
			<div>
				Dear all,
					<p>
						This is an automated mail to alert you of the submission of
						<strong style="background-color:#FFC748;text-decoration:none;">{ user_info['uploaded'] } samples by
						{ user_info['username'].split('_')[1] }</strong>.
						The pipeline to generate report has been activated and
						soon you will get another mail with all the reports.
					</p>
					<p>
					With Regards,<br>
					INSACOG DataHub
					</p>
			</div>
		"""
		message.body = html_content
		try:
			response = message.send()
			if(response):
				return "Mail sent"
			return "Mail couldn\'t be sent"
		except Exception as e:
			print(e.message)
			return "Mail couldn\'t be sent"
	else:
		print('Authentication not done')

def send_email_success(workflow_info):
	start_time = pendulum.from_format(workflow_info["upload_time"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
	end_time = pendulum.from_format(workflow_info["timestamp"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
	credentials = (os.getenv('ONEDRIVE_CLIENT'), os.getenv('ONEDRIVE_SECRET'))
	account = Account(credentials, auth_flow_type='authorization')
	if(account.is_authenticated):
		storage = account.storage()
		my_drive = storage.get_default_drive()
		search_files = my_drive.search(workflow_info["upload_time"], limit=1)
		link = ""
		for i in search_files:
			link = i.share_with_link(share_type='view').share_link
		message1 = account.new_message()
		message2 = account.new_message()
		message1.to.add(['aks1@nibmg.ac.in'])
		message2.to.add(['animesh.workplace@gmail.com'])
		# message2.to.add(['nkb1@nibmg.ac.in', 'ap3@nibmg.ac.in', 'rezwanuzzaman.laskar@gmail.com'])
		message1.subject = '📦 Report [ INSACOG DataHub ]'
		message2.subject = '📦 Report [ INSACOG DataHub ]'
		html_content1	= f"""
			<div>
				Dear all,
					<p>
						This is an automated mail to provide the link for the report generated after the submission of
						<strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['uploaded'] }
						samples by { workflow_info['username'].split('_')[1] }</strong>.<br>
						The pipeline has analyzed total
						<strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['total_seq'] } sequences</strong> and took
						<strong style="background-color:#FFC748;text-decoration:none;">{ end_time.diff(start_time).in_minutes() } minutes</strong> starting at
						<strong style="background-color:#FFC748;text-decoration:none;">{ start_time.to_day_datetime_string() }</strong> and completing at
						<strong style="background-color:#FFC748;text-decoration:none;">{ end_time.to_day_datetime_string() }</strong> to generate reports.
					</p>
					<p>
						The link contains following files:
						<ul>
							<li>Raw metadata and sequences [ Combined ]</li>
							<li>Aligned sequences using mafft</li>
							<li>Nextstrain formatted metadata and sequences [ Ready to use ]</li>
							<li>Combined metadata with all information in INSACOG DataHub metadata format</li>
							<li>Clade and Lineage report</li>
							<li>Mutation count report for all and State wise</li>
							<li>Specific VoC/VoI ID report for all and State wise</li>
							<li>Specific VoC/VoI progression report for all and State wise</li>
							<li>Lineage deletion/substitution report</li>
							<li>Logs</li>
						</ul>
					</p>
					<p>
						<a href="{ link }" target="_blank"
							style="background-color:#1b1d1e;border:1px solid #373b3e;border-radius:8px;color:#c6c1b9;display:inline-block;font-size:14px;font-weight:bold;line-height:36px;text-align:center;text-decoration:none;width:200px;"
						>
							Click here to go to Drive
						</a>
					</p>
					<p>
						With Regards,<br>
						INSACOG DataHub
					</p>
			</div>
		"""
		html_content2	= f"""
			<div>
				Dear all,
					<p>
						This is an automated mail to provide the link for the report generated after the submission of
						<strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['uploaded'] }
						samples by { workflow_info['username'].split('_')[1] }</strong>.<br>
						The pipeline has analyzed total
						<strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['total_seq'] } sequences</strong>.
					</p>
					<p>
						The link contains following files:
						<ul>
							<li>Raw metadata and sequences [ Combined ]</li>
							<li>Aligned sequences using mafft</li>
							<li>Nextstrain formatted metadata and sequences [ Ready to use ]</li>
							<li>Combined metadata with all information in INSACOG DataHub metadata format</li>
							<li>Clade and Lineage report</li>
							<li>Mutation count report for all and State wise</li>
							<li>Specific VoC/VoI ID report for all and State wise</li>
							<li>Specific VoC/VoI progression report for all and State wise</li>
							<li>Lineage deletion/substitution report</li>
							<li>Logs</li>
						</ul>
					</p>
					<p>
						<a href="{ link }" target="_blank"
							style="background-color:#1b1d1e;border:1px solid #373b3e;border-radius:8px;color:#c6c1b9;display:inline-block;font-size:14px;font-weight:bold;line-height:36px;text-align:center;text-decoration:none;width:200px;"
						>
							Click here to go to Drive
						</a>
					</p>
					<p>
						With Regards,<br>
						INSACOG DataHub
					</p>
			</div>
		"""
		message1.body = html_content1
		message2.body = html_content2
		try:
			response1 = message1.send()
			response2 = message2.send()
			if(response1 and response2):
				return "Mail sent"
			return "Mail couldn\'t be sent"
		except Exception as e:
			print(e.message)
			return "Mail couldn\'t be sent"
	else:
		print('Authentication not done')

def send_email_error(workflow_info):
	start_time = pendulum.from_format(workflow_info["upload_time"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
	end_time = pendulum.from_format(workflow_info["timestamp"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
	credentials = (os.getenv('ONEDRIVE_CLIENT'), os.getenv('ONEDRIVE_SECRET'))
	account = Account(credentials, auth_flow_type='authorization')
	if(account.is_authenticated):
		message = account.new_message()
		message.to.add(['aks1@nibmg.ac.in'])
		message.subject = f"☠️🆘☠️ Error Information [ INSACOG DataHub ]"
		html_content = f"""
			<div>
				Dear Animesh Kumar Singh,
					<p>
						This is an automated mail to alert you of an error that occured during the analysis
						and report generation which was started after the submission of
						<strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['uploaded'] } samples by
						{ workflow_info['username'].split('_')[1] }</strong>. The workflow started at
						<strong style="background-color:#FFC748;text-decoration:none;">{ start_time.to_day_datetime_string() }</strong> and error occured at
						<strong style="background-color:#FFC748;text-decoration:none;">{ end_time.to_day_datetime_string() }</strong>.
					</p>

					<p>
						Traceback of the error which occured in the step <strong style="background-color:#FFC748;text-decoration:none;">{ workflow_info['tool'] }</strong>
					</p>

					<hr>
						<pre style="font-family:'Open Sans';background-color:#E5F1DC;text-decoration:none;">{ workflow_info['message'] }</pre>
					<hr>

					<p>
					With Regards,<br>
					INSACOG DataHub
					</p>
			</div>
		"""
		message.body = html_content
		try:
			response = message.send()
			if(response):
				return "Mail sent"
			return "Mail couldn\'t be sent"
		except Exception as e:
			print(e.message)
			return "Mail couldn\'t be sent"
	else:
		print('Authentication not done')
