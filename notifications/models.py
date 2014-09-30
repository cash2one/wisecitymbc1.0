#encoding=utf8
from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils import managers

class NotificationQuerySet(models.query.QuerySet):
	
	def unread(self):
		return self.filter(unread = True)
		
	def read(self):
		return self.filter(unread = False)
		
	def mark_all_as_read(self, recipient=None):
		qs = self.unread()
		if recipient:
			qs = qs.filter(recipient=recipient)
		
		qs.update(unread=False)
	
	def mark_all_as_unread(self, recipient=None):
		qs = self.read()
		
		if recipient:
			qs = qs.filter(recipient=recipient)
			
		qs.update(unread=True)	
	
	def create_notifications(self, instances = []):
		objects = []
		for data in instances:
			objects.append(self._create(**data))
			
		return self.bulk_create(objects)
	
	def _create(self, recipient, message = '', target = None, url = '', save = False, **kwargs):
		obj = Notification(recipient = recipient, message = message, **kwargs)
		if target is not None:
			obj.target_object = target
		if not url and target is not None and hasattr(target, 'get_absolute_url'):
			url = target.get_absolute_url()
		obj.url = url
		
		if save:
			obj.save()
		return obj
		
	def create_notification(self, **kwargs):
		obj = self._create(**kwargs)
		obj.save()
		return obj
		
class NotificationManager(managers.PassThroughManager):
	pass
		
class Notification(models.Model):

	recipient = models.ForeignKey(
			'auth.User', 
			related_name = 'notifications'
	)
	
	DELETE = 'delete'
	NULL = 'null'
	ACTION_CHOICES = (
		(DELETE, 'delete'),
		(NULL, 'null'),
	)

	unread = models.BooleanField(default = True)
	important = models.BooleanField(default = False)
	
	target_content_type = models.ForeignKey(ContentType, related_name='notify_target',
		blank=True, null=True)
	target_object_id = models.CharField(max_length=255, blank=True, null=True)
	target_object = generic.GenericForeignKey('target_content_type',
		'target_object_id')
		
	created_time = models.DateTimeField(auto_now_add = True)
	message = models.TextField()
	url = models.URLField(max_length=255, null=True, blank = True)
	action = models.CharField(max_length=30, choices = ACTION_CHOICES, default = NULL, blank = True)
	
	objects = NotificationManager.for_queryset_class(NotificationQuerySet)()
	
	class Meta:
		ordering = ['-created_time','-important']
		
	def confirm(self):
		self.confirmed = True
		self.save()
		if self.action == self.DELETE and self.target_object is not None:
			self.target_object.delete()
		if not self.important:
			self.delete()
