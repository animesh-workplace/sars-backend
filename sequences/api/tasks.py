import os
import time
import arrow
import numpy
import base64
import pandas
import fuzzyset
import pendulum
import subprocess
from Bio import SeqIO
from time import sleep
from celery import shared_task
from dotenv import load_dotenv
from django.conf import settings
from django.utils import timezone
from sendgrid import SendGridAPIClient
from zipfile import ZipFile, ZIP_DEFLATED
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

@shared_task(bind=True)
def fix_metadata(self, user_info, metadata_json, timestamp):
	try:
		metadata_df = pandas.DataFrame.from_dict(metadata_json)

		# Fix State information
		all_states_indian = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry']
		fs = fuzzyset.FuzzySet(all_states_indian, False, 3, 4)
		fixed_state_name = [fs.get(i)[0][1]  for i in metadata_df['State']]
		metadata_df['State'] = fixed_state_name

		# Fix Collection date
		fixed_collection_date = [arrow.get(i, ['YYYY-MM-DD', 'DD-MM-YYYY', 'YYYY/MM/DD', 'DD/MM/YYYY', 'MM-DD-YYYY']).date() for i in metadata_df['Collection date']]
		metadata_df['Collection date'] = fixed_collection_date

		# Fix Submitting lab
		metadata_df['Submitting lab'] = user_info['username'].split('_')[1]

		# Adding Submission date and Collection month
		metadata_df['Submission date'] = metadata_df['Collection date']
		metadata_df['Collection month'] = pandas.to_datetime(metadata_df['Collection date'], format="%Y-%m-%d").dt.strftime('%b-%y')
		metadata_df['Collection week'] = [ f"{pendulum.parse(str(i)).format('MMM')}-{ pendulum.parse(str(i)).week_of_month if(pendulum.parse(str(i)).week_of_month > 0) else pendulum.parse(str(i)).week_of_month + 52 }"  for i in metadata_df['Collection date']]

		# Generate the save path
		temp = str(timezone.now()).split('.')[0]
		upload_date = temp.split(' ')[0]
		path = 'user_{0}_{1}/{2}'.format(user_info['id'], user_info['username'], upload_date)

		save_path = os.path.join(settings.MEDIA_ROOT, path)
		os.makedirs(save_path, exist_ok = True)
		save_path = os.path.join(save_path, f'fixed_metadata_{timestamp}.tsv')

		metadata_df.to_csv(save_path, sep = '\t', index = False)
		combine_metadata.delay()
		return 'Metadata Fixed & Saved'
	except:
		type_error = 'fix_metadata'
		send_email_error.delay(type_error)
		return 'Got into a error! Calling Admin'

@shared_task(bind=True)
def combine_metadata(self):
	try:
		nextstrain_labels = ['strain', 'virus', 'gisaid_epi_isl', 'genbank_accession', 'date', 'region', 'country', 'division', 'location', 'region_exposure', 'country_exposure', 'division_exposure', 'segment', 'length', 'host', 'age', 'sex', 'originating_lab', 'submitting_lab', 'authors', 'url', 'title', 'paper_url', 'date_submitted', 'purpose_of_sequencing']
		combined_metadata = pandas.DataFrame(columns = ['Virus name', 'Type', 'Passage details/history', 'Collection date', 'Collection month', 'Submission date', 'Country', 'State', 'District', 'Location', 'Additional location information', 'Host', 'Additional host information', 'Gender', 'Patient age', 'Patient status', 'Specimen source', 'Outbreak', 'Last vaccinated', 'Treatment', 'Sequencing technology', 'Assembly method', 'Coverage', 'Originating lab', 'Originating lab address', 'Submitting lab', 'Submitting lab address', 'Sample ID given by the submitting lab', 'Authors'])
		combined_sequences = []
		combined_sequences_label = []
		combined_sequences_length = []
		ignore_dir = ['user_16_test']
		ignore_file = ['template_metadata.csv', 'metadata_combined.tsv', 'nextstrain_metadata.tsv', 'sequences_combined.fasta']
		for path, dirs, files in os.walk(settings.MEDIA_ROOT):
			if(not (sum(list(map(lambda x: (x in ignore_dir), path.split('/')))) or sum(list(map(lambda x: (x in ignore_file), files))))):
				if(files):
					for i in files:
						type = i.split('_')[0]
						if(type == 'fixed'):
							metadata_url = os.path.join(path, i)
							metadata = pandas.read_csv(metadata_url, delimiter = '\t', encoding = 'utf-8', low_memory = False)
							if(not len(metadata.keys().tolist()) >= 27):
								metadata = pandas.read_csv(metadata_url, delimiter = ',', encoding = 'utf-8', low_memory = False)
							combined_metadata = pandas.concat([combined_metadata, metadata])
						elif(type == 'sequence'):
							for j in SeqIO.parse(os.path.join(path, i), 'fasta'):
								if(not j.id in combined_sequences_label):
									combined_sequences.append(j)
									combined_sequences_label.append(j.id)
									combined_sequences_length.append(len(j))

		combined_metadata['Virus name'].replace('', numpy.nan, inplace = True)
		combined_metadata.dropna(subset = ['Virus name'], inplace = True)
		combined_metadata = combined_metadata[combined_metadata['Virus name'].str.strip().astype(bool)]
		combined_metadata.reset_index(drop = True, inplace = True)
		combined_metadata.drop_duplicates(subset = ['Virus name'], ignore_index = True, inplace = True)
		nextstrain_metadata = pandas.DataFrame(columns = nextstrain_labels)
		nextstrain_metadata = nextstrain_metadata.assign(
			strain = combined_metadata['Virus name'],
			virus = combined_metadata['Type'],
			gisaid_epi_isl = [f'EPI_ISL_{i}' for i in combined_metadata.index],
			genbank_accession = ['?' for i in combined_metadata.index],
			date = combined_metadata['Collection date'],
			region = combined_metadata['Location'],
			country = combined_metadata['Country'],
			division = combined_metadata['State'],
			location = combined_metadata['District'],
			region_exposure = combined_metadata['Location'],
			country_exposure = combined_metadata['Country'],
			division_exposure = combined_metadata['State'],
			segment = ['genome' for i in combined_metadata.index],
			length = combined_sequences_length,
			host = combined_metadata['Host'],
			age = combined_metadata['Patient age'],
			sex = combined_metadata['Gender'],
			originating_lab = combined_metadata['Originating lab'],
			submitting_lab = combined_metadata['Submitting lab'],
			authors = combined_metadata['Authors'],
			url = ['?' for i in combined_metadata.index],
			title = ['?' for i in combined_metadata.index],
			paper_url = ['?' for i in combined_metadata.index],
			date_submitted = combined_metadata['Submission date'],
			purpose_of_sequencing = ['?' for i in combined_metadata.index]
		)

		SeqIO.write(combined_sequences, f'{ settings.MEDIA_ROOT }/sequences_combined.fasta', 'fasta')
		nextclade_command = f"nextclade -i { settings.MEDIA_ROOT }/sequences_combined.fasta -t { settings.MEDIA_ROOT }/clade_label.tsv"
		pangolin_update_command = f"pangolin --update"
		pangolin_command = f"pangolin { settings.MEDIA_ROOT }/sequences_combined.fasta --outfile { settings.MEDIA_ROOT }/lineage_report.csv"
		nextclade = subprocess.run(nextclade_command.split(' '))
		pangolin = subprocess.run(pangolin_update_command.split(' '))
		pangolin = subprocess.run(pangolin_command.split(' '))

		nextclade_metadata = pandas.read_csv(f'{ settings.MEDIA_ROOT }/clade_label.tsv', delimiter = '\t', encoding = 'utf-8', low_memory = False)
		pangolin_metadata = pandas.read_csv(f'{ settings.MEDIA_ROOT }/lineage_report.csv', delimiter = ',', encoding = 'utf-8', low_memory = False)

		print(nextstrain_metadata)
		print(pangolin_metadata)

		combined_metadata.to_csv(f'{ settings.MEDIA_ROOT }/metadata_combined.tsv', sep = '\t', index = False)
		nextstrain_metadata.to_csv(f'{ settings.MEDIA_ROOT }/nextstrain_metadata.tsv', sep = '\t', index = False)
		zip_obj = ZipFile(f'{ settings.MEDIA_ROOT }/combined.zip', 'w', compression = ZIP_DEFLATED, compresslevel = 9)
		zip_obj.write(f'{ settings.MEDIA_ROOT }/metadata_combined.tsv', arcname = 'metadata_combined.tsv')
		zip_obj.write(f'{ settings.MEDIA_ROOT }/nextstrain_metadata.tsv', arcname = 'nextstrain_metadata.tsv')
		zip_obj.write(f'{ settings.MEDIA_ROOT }/sequences_combined.fasta', arcname = 'sequences_combined.fasta')
		zip_obj.close()
		# send_email_general.delay('Insacog_NIBMG', 20)
		return 'Combined all metadata and fasta'
	except:
		type_error = 'combine_metadata'
		send_email_error.delay(type_error)
		return 'Got into a error! Calling Admin'

@shared_task(bind=True)
def send_email_error(self, type_error):
	message = Mail(
		from_email		= os.getenv('SENDGRID_EMAIL'),
		to_emails		= ('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
		subject 		= f'🆘INSACOG DataHub automated mail: Error Information {type_error}',
		html_content	= f"""
			<div>
				<strong>Dear Animesh Kumar Singh,</strong>
					<p>
						This is an automated mail to alert you of an error that occured during the generation of
						combined fasta/metadata. Manually run the fix_metadata and combine_metadata function.
					</p>
					<p>
					With Regards,<br>
					INSACOG DataHub
					</p>
			</div>
		"""
		)
	try:
		sg = SendGridAPIClient(os.getenv('SENDGRID_API'))
		response = sg.send(message)
		return 'Mail sent'
	except Exception as e:
		print(e.message)
		return 'Mail couldnot be sent'

@shared_task(bind=True)
def send_email_general(self, username, count):
	mailing_list = [
		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
		# ('sahinshaagt2010@gmail.com', 'Check animesh')
	]
	error = None
	with open(f'{ settings.MEDIA_ROOT }/combined.zip', 'rb') as f:
		data = f.read()
	encoded = base64.b64encode(data).decode()

	attached_file = Attachment()
	print(dir(attached_file))
	attached_file.file_content = encoded
	attached_file.file_type = "application/zip"
	attached_file.file_name = "combined.zip"
	attached_file.disposition = "attachment"

	for i in mailing_list:
		message = Mail(
			from_email		= os.getenv('SENDGRID_EMAIL'),
			to_emails		= i,
			subject 		= '⚡INSACOG DataHub automated mail: Upload Information',
			html_content	= f"""
				<div>
					<strong>Dear { i[1] },</strong>
						<p>
							This is an automated mail to alert you of the deposition of
							<strong>{ count } samples by { username.split('_')[1] }</strong>.
							The pipeline to generate report has been activated and
							soon you will get another mail with the combined metadata and fasta.
						</p>
						<p>
						With Regards,<br>
						INSACOG DataHub
						</p>
				</div>
			"""
			)
		message.add_attachment(attached_file)
		try:
			sg = SendGridAPIClient(os.getenv('SENDGRID_API'))
			response = sg.send(message)
		except Exception as e:
			error = 1
			print(e.message)

	if(not error):
		return 'Mail Sent'
	else:
		return 'Mail could not be sent'
