import pendulum
import jsonfield
from django.db import models
from django.conf import settings
from django.utils import timezone
from .storage import OverwriteStorage

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
	submission_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
	metadata 		= jsonfield.JSONField()

class Download_Handler(models.Model):
	creation_date = models.DateTimeField(auto_now=True)
	download_link = models.CharField(max_length=500, blank=True)

class Frontend_Handler(models.Model):
	metadata = jsonfield.JSONField()
	map_data = jsonfield.JSONField()
	genomes_sequenced = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	variants_catalogued = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	lineages_catalogued = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	states_covered = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)


