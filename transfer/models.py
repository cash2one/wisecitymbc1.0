from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common.fields import DecimalField
from common.mixins import get_inc_dec_mixin

class Deposit(get_inc_dec_mixin(['money'])):

	bank = models.ForeignKey('accounts.Bank', related_name = 'stored_deposits')
	
	owner_content_type = models.ForeignKey(ContentType, related_name='deposit_owner')
	owner_object_id = models.CharField(max_length=255)
	owner = generic.GenericForeignKey('owner_content_type', 'owner_object_id')
	
	money = DecimalField()
	
	class Meta:
		permissions = (
			('can_store', 'Can store'),
		)
	
class TransferLog(models.Model):

	transfer_by_content_type = models.ForeignKey(ContentType, related_name='transfer_by')
	transfer_by_object_id = models.CharField(max_length=255)
	transfer_by = generic.GenericForeignKey('transfer_by_content_type', 'transfer_by_object_id')
	
	transfer_to_content_type = models.ForeignKey(ContentType, related_name='transfer_to')
	transfer_to_object_id = models.CharField(max_length=255)
	transfer_to = generic.GenericForeignKey('transfer_to_content_type', 'transfer_to_object_id')
	
	money = DecimalField()
	created_time = models.DateTimeField(auto_now_add = True)
	
	class Meta:
		ordering = ['-created_time']
		permissions = (
			('can_transfer', 'Can transfer'),
		)
