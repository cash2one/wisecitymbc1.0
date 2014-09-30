#encoding=utf8
from django.db import models
from django.conf import settings
from .storage import SAEStorage

import os

class File(models.Model):
	
	PRIVATE = 'private'
	PUBLIC  = 'public'
	FILE_TYPE_CHOICES = (
			(PRIVATE, 'private'),
			(PUBLIC,  'public'),
	)
	
	created_time = models.DateTimeField(auto_now_add = True)
	file = models.FileField(
			upload_to = '%s/'%settings.PATH_DATETIME_FORMAT, 
			storage = SAEStorage(settings.SAE_FILE_STORAGE_DOMAIN_NAME)
	)
	file_type = models.CharField(max_length = 7, choices = FILE_TYPE_CHOICES)
	
	def delete(self, *args, **kwargs):
		self.file.delete()
		super(File, self).delete(*args, **kwargs)
	
	def __unicode__(self):
		return u"文件 %s" % os.path.basename(self.file.name)
	
	class Meta:
		ordering = ['-created_time']
		permissions = (
			('has_report', 'Has report'),
		)

class PublicFileManager(models.Manager):
	
	def get_query_set(self):
		return super(PublicFileManager, self).get_query_set().filter(file_type = File.PUBLIC)
		
class PublicFile(File):

	objects = PublicFileManager()

	class Meta:
		proxy = True
		
class PrivateFileManager(models.Manager):
	
	def get_query_set(self):
		return super(PrivateFileManager, self).get_query_set().filter(file_type = File.PRIVATE)
		
class PrivateFile(File):
	
	objects = PrivateFileManager()
	
	class Meta:
		proxy = True
