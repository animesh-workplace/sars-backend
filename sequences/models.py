import pendulum
# import jsonfield
from django.db import models
from django.conf import settings
from django.db import connection
from django.utils import timezone
from .storage import OverwriteStorage
from django.db.models import JSONField

# Create your functions here
def user_directory_path(instance, filename):
	# File will be uploaded to MEDIA_ROOT/Uploaded_data/user_<id>_<username>/file/<filename>
	save_time = pendulum.now().to_datetime_string().split(' ')[0]
	return 'Uploaded_data/user_{0}_{1}/{2}/{3}'.format(instance.user.id, instance.user, save_time, filename)

# Create your models here.
class File_Handler(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
	metadata 		= models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), verbose_name='Metadata')
	sequences 		= models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), verbose_name='Sequence')

class Metadata_Handler(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
	metadata 		= JSONField()
	submission_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)

class Download_Handler(models.Model):
	creation_date = models.DateTimeField(auto_now=True)
	download_link = models.CharField(max_length=500, blank=True)

class Frontend_Handler(models.Model):
	map_data 			= JSONField()
	last_updated 		= models.DateTimeField(auto_now=True)
	pie_chart_data 		= JSONField()
	states_covered 		= models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	pangolin_version 	= models.CharField(max_length=255)
	genomes_sequenced 	= models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	nextclade_version 	= models.CharField(max_length=255)
	pangolearn_version 	= models.CharField(max_length=255)
	variants_catalogued = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	lineages_catalogued = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)

class Metadata(models.Model):
	State 					= models.CharField(max_length=255)
	Clade 					= models.CharField(max_length=255)
	Gender 					= models.CharField(max_length=255, blank=True, null=True)
	Lineage 				= models.CharField(max_length=255)
	District 				= models.CharField(max_length=255, blank=True, null=True)
	Deletions 				= models.TextField()
	Treatment 				= models.CharField(max_length=255, blank=True, null=True)
	Virus_name 				= models.CharField(max_length=255)
	aaDeletions 			= models.TextField()
	Patient_age 			= models.CharField(max_length=255, blank=True, null=True)
	Scorpio_call 			= models.CharField(max_length=255, blank=True, null=True)
	Substitutions 			= models.TextField()
	Submitting_lab 			= models.CharField(max_length=255, blank=True, null=True)
	Patient_status 			= models.CharField(max_length=255, blank=True, null=True)
	Collection_date 		= models.CharField(max_length=255, blank=True, null=True)
	Last_vaccinated 		= models.CharField(max_length=255, blank=True, null=True)
	Originating_lab 		= models.CharField(max_length=255, blank=True, null=True)
	Assembly_method 		= models.CharField(max_length=255, blank=True, null=True)
	aaSubstitutions 		= models.TextField()
	Sequencing_technology 	= models.CharField(max_length=255, blank=True, null=True)

	@classmethod
	def truncate(cls):
		with connection.cursor() as cursor:
			cursor.execute(f'DELETE FROM {cls._meta.db_table}')
