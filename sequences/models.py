import pendulum
import jsonfield
from django.db import models
from django.conf import settings
from django.utils import timezone
from .storage import OverwriteStorage

# Create your functions here
def user_directory_path(instance, filename):
	# File will be uploaded to MEDIA_ROOT/user_<id>_<username>/file/<filename>
	save_time = pendulum.now().to_datetime_string().split(' ')[0]
	return 'user_{0}_{1}/{2}/{3}'.format(instance.user.id, instance.user, save_time, filename)

# Create your models here.
class File_Handler(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
	metadata 		= models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), verbose_name='Metadata')
	sequences 		= models.FileField(upload_to=user_directory_path, storage=OverwriteStorage(), verbose_name='Sequence')

class Metadata_Handler(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
	submission_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
	metadata 		= jsonfield.JSONField()
