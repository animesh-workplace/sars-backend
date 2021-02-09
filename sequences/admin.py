from .models import *
from django.contrib import admin

# Register your models here.
class File_Handler_Manager(admin.ModelAdmin):
	list_display = ('user', 'metadata')

class Metadata_Handler_Manager(admin.ModelAdmin):
	list_display = ('user', 'submission_date')

admin.site.register(File_Handler, File_Handler_Manager)
admin.site.register(Metadata_Handler, Metadata_Handler_Manager)
