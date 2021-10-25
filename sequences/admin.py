from .models import *
from django.contrib import admin

# Register your models here.
class File_Handler_Manager(admin.ModelAdmin):
	list_display = ('user', 'metadata')

class Metadata_Handler_Manager(admin.ModelAdmin):
	list_display = ('user', 'submission_date')

class Download_Handler_Manager(admin.ModelAdmin):
	list_display = ('creation_date', 'download_link')

class Frontend_Handler_Manager(admin.ModelAdmin):
	list_display = ('id', 'last_updated')

class Metadata_Manager(admin.ModelAdmin):
	list_display = ('Virus_name', 'Submitting_lab' ,'Clade', 'Lineage', 'Scorpio_call')

admin.site.register(Metadata, Metadata_Manager)
admin.site.register(File_Handler, File_Handler_Manager)
admin.site.register(Metadata_Handler, Metadata_Handler_Manager)
admin.site.register(Download_Handler, Download_Handler_Manager)
admin.site.register(Frontend_Handler, Frontend_Handler_Manager)
