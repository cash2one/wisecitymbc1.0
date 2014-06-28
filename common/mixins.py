from django.db import models
from common.fields import DecimalField
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from functools import partial
from exceptions import AssetsNotEnough

def get_inc_dec_mixin(fields = []):

	class IncDecMixin(models.Model):
		
		def __set_item(self, field_name, value, commit = True, reload = False, enable_pre = True, enable_post = True):
			if enable_pre:
				pre = getattr(self, 'pre_set_%s' % field_name, None)
				if pre is not None:
					pre(value)
			
			if self.id is None:
				setattr(self, field_name, value)
				if commit:
					self.save()
			else:
				setattr(self, field_name, getattr(self, field_name)+Decimal(value))
				if commit:
					self.save()
				if reload:
					self = self.__class__.objects.get(pk = self.id)
					
			if enable_post:
				post = getattr(self, 'post_set_%s' % field_name, None)
				if post is not None:
					post(value)
			
		def __inc(self, field_name, value, commit = True, reload = False):
			return self.__set_item(field_name, value, commit, reload)
			
		def __dec(self, field_name, value, commit = True, reload = False):
			return self.__set_item(field_name, -value, commit, reload)
		
		def __getattr__(self, name):
			action, field_name = name[:3], name[4:]
			if field_name not in fields or action not in ('inc', 'dec'):
				raise AttributeError, name
				
			if action == 'inc':
				return partial(self.__inc, field_name)
			else:
				return partial(self.__dec, field_name)
		
		class Meta:
			abstract = True
		
	return IncDecMixin

class HasAssetsMixin(get_inc_dec_mixin(['assets'])):
	
	assets = DecimalField()
	
	def check_assets(self, assets):
		print self.assets, assets
		if self.assets < Decimal(assets):
			return False
		
		return True
	
	class Meta:
		abstract = True
