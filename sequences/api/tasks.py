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
def create_config_file(self, upload_info):
	upload_date = pendulum.now('Asia/Kolkata').format('YYYY-MM-DD_hh_mm_ss_A')
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
def send_email_general(self, username, count, total_length):
	mailing_list = [
		('aks1@nibmg.ac.in', 'Animesh Kumar Singh'),
		# ('nkb1@nibmg.ac.in', 'Dr. Nidhan Biswas'),
		# ('ap3@nibmg.ac.in', 'Antara Paul'),
		# ('rezwanuzzaman.laskar@gmail.com', 'Rezwanuzzaman Laskar')
	]
	message = Mail(
		from_email		= os.getenv('SENDGRID_EMAIL'),
		to_emails		= mailing_list,
		subject 		= '[TEST]⚡INSACOG DataHub automated mail: Upload Information',
		html_content	= f"""
			<div>
				<strong>Dear all,</strong>
					<p>
						This is an automated mail to alert you of the deposition of
						<strong>{ count } samples by { username.split('_')[1] }</strong>.
						The pipeline to generate report has been activated and
						soon you will get another mail with all the reports. Please find attached with
						this mail a zip containing combined metadata (General and Nextstrain) and combined sequences
						<strong>(Total = { total_length })</strong>.
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
	except Exception as e:
		error_traceback = traceback.format_exc()
		print(error_traceback)
		return 'Mail could not be sent'

	return 'Mail Sent'
