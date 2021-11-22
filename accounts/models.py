import os
from django.db import models
from dotenv import load_dotenv
from django.conf import settings
from .storage import OverwriteStorage
from django.contrib.auth.models import AbstractUser

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

# Create your models here.
class Accounts(AbstractUser):
	state			= models.CharField(blank=True, max_length=255)
	city			= models.CharField(blank=True, max_length=255)
	export 			= models.BooleanField(default=False, verbose_name='Export status')
	address			= models.CharField(blank=True, max_length=1000)
	download 		= models.BooleanField(default=False, verbose_name='Download status')
	pin_code		= models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
	last_name 		= models.CharField(max_length=255, blank=True)
	institute		= models.CharField(blank=True, max_length=500)
	first_name 		= models.CharField(max_length=255, blank=True)
