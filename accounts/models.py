import os
from django.db import models
from dotenv import load_dotenv
from django.conf import settings
from .storage import OverwriteStorage
from django.contrib.auth.models import AbstractUser

load_dotenv(os.path.join(settings.BASE_DIR, '.env'))

# Create your models here.
class Accounts(AbstractUser):
	first_name 		= models.CharField(max_length=255, blank=True)
	last_name 		= models.CharField(max_length=255, blank=True)
	institute		= models.CharField(blank=True, max_length=500)
	state			= models.CharField(blank=True, max_length=255)
	city			= models.CharField(blank=True, max_length=255)
	address			= models.CharField(blank=True, max_length=1000)
	pin_code		= models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
