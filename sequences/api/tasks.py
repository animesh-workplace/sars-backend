import os
import time
import yaml
import arrow
import numpy
import base64
import pandas
import fuzzyset
import pendulum
import subprocess
import collections
from Bio import SeqIO
from time import sleep
from O365 import Account
from celery import shared_task
from dotenv import load_dotenv
from django.conf import settings
from django.utils import timezone
from zipfile import ZipFile, ZIP_DEFLATED
# from sendgrid import SendGridAPIClient
# from .ssh_job_submission import RemoteClient
# from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

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
	command = f"exec snakemake --snakefile {snakefile_loc} --configfile {configfile_loc} --cores 4"
	snakemake_command = subprocess.run(command, shell = True)
	return 'Pipeline run completed'

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
		for i in search_files:
			link = i.share_with_link(share_type='view').share_link
		message = account.new_message()
		# message.to.add(['aks1@nibmg.ac.in', 'nkb1@nibmg.ac.in', 'ap3@nibmg.ac.in', 'rezwanuzzaman.laskar@gmail.com'])
		message.to.add(['aks1@nibmg.ac.in'])
		message.subject = '📦 Report [ INSACOG DataHub ]'
		html_content	= f"""
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
							style="background-color:#1b1d1e;border:1px solid #373b3e;border-radius:18px;color:#c6c1b9;display:inline-block;font-size:13px;font-weight:bold;line-height:36px;text-align:center;text-decoration:none;width:200px;"
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

# def send_email_upload(user_info):
# 	mailing_list = [
# 		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
# 		# ('nkb1@nibmg.ac.in', 'Dr. Nidhan Biswas'),
# 		# ('ap3@nibmg.ac.in', 'Antara Paul'),
# 		# ('rezwanuzzaman.laskar@gmail.com', 'Rezwanuzzaman Laskar')
# 	]
# 	message = Mail(
# 		from_email		= os.getenv('SENDGRID_EMAIL'),
# 		to_emails		= mailing_list,
# 		subject 		= '✅|📤 Upload Info [ INSACOG DataHub Test Hub ]',
# 		html_content	= f"""
# 			<div>
# 				Dear all,
# 					<p>
# 						This is an automated mail to alert you of the submission of
# 						<strong style="background-color:#FFC748;">{ user_info['uploaded'] } samples by
# 						{ user_info['username'].split('_')[1] }</strong>.
# 						The pipeline to generate report has been activated and
# 						soon you will get another mail with all the reports.
# 					</p>
# 					<p>
# 					With Regards,<br>
# 					INSACOG DataHub
# 					</p>
# 			</div>
# 		"""
# 		)
# 	try:
# 		sg = SendGridAPIClient(os.getenv('SENDGRID_API'))
# 		response = sg.send(message)
# 	except Exception as e:
# 		error_traceback = traceback.format_exc()
# 		print(error_traceback)
# 		return "Mail couldn\'t be sent"

# 	return "Mail Sent"


# def send_email_success(workflow_info):
# 	start_time = pendulum.from_format(workflow_info["upload_time"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
# 	end_time = pendulum.from_format(workflow_info["timestamp"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
# 	mailing_list = [
# 		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
# 		# ('nkb1@nibmg.ac.in', 'Dr. Nidhan Biswas'),
# 		# ('ap3@nibmg.ac.in', 'Antara Paul'),
# 		# ('rezwanuzzaman.laskar@gmail.com', 'Rezwanuzzaman Laskar')
# 	]
# 	message = Mail(
# 		from_email		= os.getenv('SENDGRID_EMAIL'),
# 		to_emails		= mailing_list,
# 		subject 		= '📦 Report [ INSACOG DataHub Test Hub ]',
# 		html_content	= f"""
# 			<div>
# 				Dear all,
# 					<p>
# 						This is an automated mail to provide the link for the report generated after the submission of
# 						<strong style="background-color:#FFC748;">{ workflow_info['uploaded'] }
# 						samples by { workflow_info['username'].split('_')[1] }</strong>.<br>
# 						The pipeline has analyzed total
# 						<strong style="background-color:#FFC748;">{ workflow_info['total_seq'] } sequences</strong> and took
# 						<strong style="background-color:#FFC748;">{ end_time.diff(start_time).in_minutes() } minutes</strong> starting at
# 						<strong style="background-color:#FFC748;">{ start_time.to_day_datetime_string() }</strong> and completing at
# 						<strong style="background-color:#FFC748;">{ end_time.to_day_datetime_string() }</strong> to generate reports.
# 					</p>

# 					<p>
# 						The link contains following files:
# 						<ul>
# 							<li>Raw metadata and sequences [ Combined ]</li>
# 							<li>Aligned sequences using mafft</li>
# 							<li>Nextstrain formatted metadata and sequences [ Ready to use ]</li>
# 							<li>Combined metadata with all information in INSACOG DataHub metadata format</li>
# 							<li>Clade and Lineage report</li>
# 							<li>Mutation count report for all and State wise</li>
# 							<li>Specific VoC/VoI ID report for all and State wise</li>
# 							<li>Specific VoC/VoI progression report for all and State wise</li>
# 							<li>Lineage deletion/substitution report</li>
# 							<li>Logs</li>
# 						</ul>
# 					</p>

# 					<p>
# 						With Regards,<br>
# 						INSACOG DataHub
# 					</p>
# 			</div>
# 		"""
# 		)
# 	try:
# 		sg = SendGridAPIClient(os.getenv('SENDGRID_API'))
# 		response = sg.send(message)
# 	except Exception as e:
# 		error_traceback = traceback.format_exc()
# 		print(error_traceback)
# 		return "Mail couldn\'t be sent"

# 	return "Mail Sent"

# def send_email_error(workflow_info):
# 	start_time = pendulum.from_format(workflow_info["upload_time"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
# 	end_time = pendulum.from_format(workflow_info["timestamp"], "YYYY-MM-DD_hh-mm-ss-A", tz="Asia/Kolkata")
# 	mailing_list = [
# 		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
# 	]
# 	message = Mail(
# 		from_email		= os.getenv('SENDGRID_EMAIL'),
# 		to_emails		= mailing_list,
# 		subject 		= f'☠️🆘☠️ Error Information [ INSACOG DataHub Test Hub ]',
# 		html_content	= f"""
# 			<div>
# 				Dear Animesh Kumar Singh,
# 					<p>
# 						This is an automated mail to alert you of an error that occured during the analysis
# 						and report generation which was started after the submission of
# 						<strong style="background-color:#FFC748;">{ workflow_info['uploaded'] } samples by
# 						{ workflow_info['username'].split('_')[1] }</strong>. The workflow started at
# 						<strong style="background-color:#FFC748;">{ start_time.to_day_datetime_string() }</strong> and error occured at
# 						<strong style="background-color:#FFC748;">{ end_time.to_day_datetime_string() }</strong>.
# 					</p>

# 					<p>
# 						Traceback of the error which occured in the step <strong style="background-color:#FFC748;">{ workflow_info['tool'] }</strong>
# 					</p>

# 					<hr>
# 						<pre style="font-family:'Open Sans';background-color:#E5F1DC;">{ workflow_info['message'] }</pre>
# 					<hr>

# 					<p>
# 					With Regards,<br>
# 					INSACOG DataHub
# 					</p>
# 			</div>
# 		"""
# 		)
# 	try:
# 		sg = SendGridAPIClient(os.getenv('SENDGRID_API'))
# 		response = sg.send(message)
# 		return "Mail sent"
# 	except Exception as e:
# 		print(e.message)
# 		return "Mail couldn\'t be sent"

