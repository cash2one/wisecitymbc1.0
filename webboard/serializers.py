from django.core.urlresolvers import reverse
from rest_framework import serializers, pagination
import models
from django.contrib.auth.models import User
import accounts.serializers
from files.serializers import FileField
from common.serializers import WritableRelatedField

class PassageSerializer(serializers.ModelSerializer):

	author = WritableRelatedField(serializer_class = accounts.serializers.UserSerializer)
	attachments = FileField(type = 'public', many = True, required = False)
	url = serializers.SerializerMethodField('get_url')
	
	def get_url(self, obj):
		return '/webboard/passages/%d/' % obj.id
	class Meta:
		model = models.Passage
		
class CommentSerializer(serializers.ModelSerializer):
	
	author = WritableRelatedField(serializer_class = accounts.serializers.UserSerializer)
	passage = serializers.PrimaryKeyRelatedField(write_only = True)
	
	class Meta:
		model = models.Comment
		
class PaginatedCommentSerializer(pagination.PaginationSerializer):

	class Meta:
		object_serializer_class = CommentSerializer
