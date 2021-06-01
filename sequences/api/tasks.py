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
from celery import shared_task
from dotenv import load_dotenv
from django.conf import settings
from django.utils import timezone
from sendgrid import SendGridAPIClient
from zipfile import ZipFile, ZIP_DEFLATED
from .ssh_job_submission import RemoteClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

@shared_task(bind=True)
def fix_metadata(self, user_info, metadata_json, timestamp):
	try:
		upload_info = {
			'username': user_info['username'],
			'uploaded': len(metadata_json)
		}
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
		upload_date = pendulum.now().to_datetime_string().split(' ')[0]
		path = 'user_{0}_{1}/{2}'.format(user_info['id'], user_info['username'], upload_date)

		save_path = os.path.join(settings.MEDIA_ROOT, path)
		os.makedirs(save_path, exist_ok = True)
		save_path = os.path.join(save_path, f'fixed_metadata_{timestamp}.tsv')

		metadata_df.to_csv(save_path, sep = '\t', index = False)
		config_date = pendulum.now().to_datetime_string().replace(' ', '_')
		create_config_file.delay(upload_info, config_date)
		return 'Metadata Fixed & Saved'
	except:
		type_error = 'fix_metadata'
		send_email_error.delay(type_error)
		return 'Got into a error! Calling Admin'

@shared_task(bind=True)
def create_config_file(self, upload_info, upload_date):
	upload_date = pendulum.now().to_datetime_string().replace(' ', '_')
	config_data = {
		"analysis_time": upload_date,
		"base_path": settings.MEDIA_ROOT,
		"uploaded_by": upload_info['username'],
		"sequences_uploaded": upload_info['uploaded'],
	}
	configfile_loc = os.path.join(settings.BASE_DIR, 'workflow', 'config', f"config_{upload_date}.yaml")
	yaml.dump(config_data, open(configfile_loc, 'w'))
	run_pipeline()

def run_pipeline():
	configfile_loc = os.path.join(settings.BASE_DIR, 'workflow', 'config', 'config.yaml')
	snakefile_loc = os.path.join(settings.BASE_DIR, 'workflow', 'Snakefile')
	command = f"exec snakemake --snakefile {snakefile_loc} --configfile {configfile_loc} --cores 4"
	snakemake_command = subprocess.run(command, shell = True)
	return 'Pipeline run completed'

@shared_task(bind=True)
def send_email_error(self, type_error):
	message = Mail(
		from_email		= os.getenv('SENDGRID_EMAIL'),
		to_emails		= ('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
		subject 		= f'🆘INSACOG DataHub automated mail: Error Information {type_error} Test Hub',
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
def send_email_general(self, username, count, path, total_length):
	mailing_list = [
		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
		# ('nkb1@nibmg.ac.in', 'Dr. Nidhan Biswas'),
		# ('paul.antara02@gmail.com', 'Antara Paul')
	]
	error = None
	with open(f'{path}/combined.zip', 'rb') as f:
		data = f.read()
	encoded = base64.b64encode(data).decode()

	attached_file = Attachment()
	attached_file.file_content 	= encoded
	attached_file.disposition 	= "attachment"
	attached_file.file_name 	= "combined.zip"
	attached_file.file_type 	= "application/zip"

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
							soon you will get another mail with all the reports. Please find attached with
							this mail a zip containing combined metadata (General and Nextstrain) and combined sequences
							<strong>(Total = {total_length})</strong>.
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
