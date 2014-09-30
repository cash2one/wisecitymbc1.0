from rest_framework import serializers
from models import PrivateFile, PublicFile,	File
import os.path

class FileField(serializers.FileField):

	encode_file = lambda self, obj:{
			"name": os.path.basename(obj.file.name),
			"url":obj.file.url,
			"id": obj.id,
			"created_time": obj.created_time
	}

	def	__init__(self, *args, **kwargs):
		self.type = kwargs.pop('type', 'private')
		assert self.type in ('public','private')
		self.many = kwargs.pop('many', False)
		super(FileField, self).__init__(*args, **kwargs) 
		
	def from_native(self, value):
		cls = self.type == 'private' and PrivateFile or PublicFile
		if self.many:
			assert isinstance(value, (tuple, list))
			return cls.objects.filter(pk__in =	value)
		else:
			assert isinstance(value, (str, int))
			return cls.objects.get(pk = value)
		
	def to_native(self, value):
		if self.many:
			return FileSerializer(value.all(), many = self.many).data
		else:
			return FileSerializer(value).data

class FileSerializer(serializers.ModelSerializer):

	file_type = serializers.CharField(write_only = True)
	name = serializers.SerializerMethodField('get_file')
	file = serializers.FileField(write_only = True)
	url  = serializers.Field(source = 'file.url')
	created_time = serializers.DateTimeField(read_only = True)
	
	def get_file(self, obj):
		return os.path.basename(obj.file.name)
		
	class Meta:
		model = File

class PrivateFileSerializer(FileSerializer):

	class Meta:
		model = PrivateFile
		
class PublicFileSerializer(FileSerializer):
	
	class Meta:
		model = PublicFile
