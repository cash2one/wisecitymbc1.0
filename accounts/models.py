#coding=utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ObjectDoesNotExist
from files.storage import SAEStorage

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common.fields import DecimalField
from files.models import PrivateFile, PublicFile, File
from annoying.fields import AutoOneToOneField

from django.db import connection

import managers
from inspect import getmro

from common.mixins import HasAssetsMixin
from securities.mixins import *
from transfer.mixins import *
from webboard.mixins import *

# Abstract logical interfaces.

__accounts__ = ['Bank', 'Company', 'Fund', 'FundCompany', 'Government', 'Media', 'Person']

class HasReportsMixin(object):
	
	permission = 'has_report'
	
	@classmethod
	def has_field(cls, field_name):
		try:
			return cls._meta.get_field_by_name(field_name)
		except:
			pass
	
	def upload_reports(self, file_ids, **kwargs):
		field_name = kwargs.pop('field_name',self.report_field)
		field = self.has_field(field_name)
		if not field:
			return
		
		objects = PrivateFile.objects.only('pk')
		if isinstance(file_ids, (list, tuple)):
			files = objects.filter(pk__in = file_ids) if isinstance(file_ids, (str,int)) else files
		elif isinstance(file_ids, (int, str)):
			files = objects.filter(pk = int(file_ids))
		else:
			files = (file_ids,)

		if isinstance(field, models.ForeignKey):
			setattr(self, field_name, files[0])
			self.save()
		else:
			getattr(self, field_name).add(*files)
		
# Models definition.
	
class UserProfile(models.Model):
	
	user = AutoOneToOneField(User, unique = True, related_name = 'profile')
	
	info_type = models.ForeignKey(ContentType, null = True, blank = True)
	info_object_id = models.PositiveIntegerField(null = True, blank = True)
	info_object = generic.GenericForeignKey('info_type', 'info_object_id')
	
	def __unicode__(self):
		return u"%s 的个人信息" % self.user.username
	
	def create_info(self, class_name, save = True, **kwargs):
		if self.info_object is None:
			cls = globals().get(class_name, None) or account_classes_map.get(class_name)
			self.info_object = cls.objects.create(**kwargs)
			permission_names = [getattr(cls, 'permission', '') for cls in filter(lambda cls:cls.__name__.endswith('Mixin'), getmro(cls))]
			permissions = Permission.objects.filter(codename__in = permission_names)
			self.user.user_permissions.add(*permissions)
			self.user.save()
			if save:
				self.save()
		return self.info_object
	
	@property
	def info(self):
		return self.info_object
			
	@info.setter
	def info(self, obj):
		if self.user.is_staff:
			return
		self.info_object = obj			
		
class Account(models.Model):
	
	display_name = models.CharField(max_length = 50, default = '', blank = True)
	profile_object = generic.GenericRelation(
			'UserProfile',
			content_type_field = 'info_type',
			object_id_field = 'info_object_id'
	)
	
	def __unicode__(self):
		return self.display_name
		
	def get_groups(self):
		return []
	
	@property
	def profile(self):
		return self.profile_object.all()[0]
		
	@property
	def account_type(self):
		return self.__class__.__name__.lower()
	
	class Meta:
		abstract = True
	
class PersonalModel(Account, HasAssetsMixin, HasFundMixin, CanTransferMixin):

	MALE = 'M'
	FEMALE = 'F'
	GENDER_CHOICE = (
			(MALE, 'male'),
			(FEMALE, 'female'),
	)
	
	gender = models.CharField(max_length = 1, default = MALE, blank = True)
	position = models.CharField(max_length = 20, default = '', blank = True)
	
	class Meta:
		abstract = True
	
class Media(Account, CanWriteMixin):
	
	contact = models.CharField(max_length = 20, default = '')	
	
	def get_groups(self):
		return ['writer']
		
class Person(PersonalModel, HasReportsMixin, HasStockBondMixin, CanStoreMixin):

	company_type = models.ForeignKey(ContentType, null = True, blank = True)
	company_object_id = models.PositiveIntegerField(null = True, blank = True)
	company = generic.GenericForeignKey('company_type', 'company_object_id')
	industry = models.CharField(max_length = 255, default = '', blank = True)
	debt_files = models.ManyToManyField(PrivateFile, related_name = 'debt_files_owners')
	consumption_reports = models.ManyToManyField(PrivateFile, related_name = 'consumption_reports_owners')
	
	report_field = 'consumption_reports'
	
	def save(self, *args, **kwargs):
		if self.id is None or not self.industry:
			self.industry = self.company.industry
		super(Person, self).save(*args, **kwargs)
	
class Government(PersonalModel, HasStockBondMixin, CanWriteMixin):

	def get_groups(self):
		return ('writer',)
	
class Enterprise(Account, HasAssetsMixin, HasReportsMixin, 
		HasStockBondMixin, HasFundMixin, CanTransferMixin, CanWriteMixin, OwnBondMixin, OwnStockMixin):

	description = models.CharField(max_length = 255, default = '', blank = True)
	contact = models.CharField(max_length = 20, default = '', blank = True)
	financial_reports = models.ManyToManyField(PrivateFile, related_name = '%(class)ss')

	members = generic.GenericRelation(
			'Person',
			content_type_field = 'company_type',
			object_id_field = 'company_object_id'
	)	
	
	report_field = 'financial_reports'
	
	def get_groups(self):
		return ('writer',)
	
	class Meta:
		abstract = True
		
class Company(Enterprise,CanStoreMixin):

	industry = models.CharField(max_length = 255, default = '', blank = True)
	section = models.CharField(max_length = 255, default = '', blank = True)
	
class FundCompany(Enterprise, OwnFundMixin):

	pass
	
class Bank(Enterprise, OwnFundMixin):
	
	rate = DecimalField()
	
	def share_profits(self):
		rate = self.rate /100
		cursor = connection.cursor()
		cursor.execute(
				"""UPDATE transfer_deposit SET money = ROUND(money*(1+%s), 4) WHERE bank_id=%d""" % (rate, self.id) 
		)
	
class Fund(Account, HasAssetsMixin):

	pass
	
__account_classes = map(lambda x: globals()[x], __accounts__)
account_classes_map = {x.__name__.lower(): x for x in __account_classes}
__tables = [(cls.__name__.lower(), cls._meta.db_table) for cls in __account_classes]
from django.db import connection
	

def get_enterprises():
	result = []
	for cls in (Company, FundCompany, Bank):
		result.extend(cls.objects.all())
	
	return result
	
def filter_accounts(**kwargs):
	sql = 'SELECT * FROM (%s) as t ' % ' UNION '.join('(SELECT "%s" as account_type, id, display_name FROM %s)' % (data[0], data[1]) for data in __tables)
	if kwargs:
		args = []
		for key, value in kwargs.iteritems():
			if isinstance(value, (str, unicode)):
				args.append('%s="%s"' % (key, value))#(key, '"%s"' % value))
			elif isinstance(value, (tuple, list)):
				args.append("%s IN (%s)" % (key, ",".join(map(lambda x:'"%s"' % x, value))))
			else:
				args.append('%s=%s' % (key, value))
		condition = ' AND '.join(args)
		sql = '%s WHERE %s' % (sql, condition)
		
	print sql	
		
	cursor = connection.cursor()
	cursor.execute(sql)
	res = cursor.fetchall()
	res = map(lambda a:{"account_type": a[0], "id": a[1], "display_name": a[2], "class": account_classes_map[a[0]]}, res)
	return res
