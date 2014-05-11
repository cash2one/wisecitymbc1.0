#coding=utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from common.storage import SAEStorage

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common import fields
from file_upload.models import PrivateFile, PublicFile
from annoying.fields import AutoOneToOneField
	
import managers
	
class HasReportModel(object):
	
	def upload_reports(self, file_ids):
		objects = PrivateFile.objects.only('pk')
		if isinstance(file_ids, (list, tuple)):
			files = objects.filter(pk__in = file_ids)
		else:
			files = objects.filter(pk = int(file_ids))
			
		getattr(self, self.report_field).add(*files)
	
class UserProfile(models.Model):
	
	user = AutoOneToOneField(User, unique = True, related_name = 'profile')
	
	info_type = models.ForeignKey(ContentType, null = True, blank = True)
	info_object_id = models.PositiveIntegerField(null = True, blank = True)
	info_object = generic.GenericForeignKey('info_type', 'info_object_id')
	
	@property
	def info(self):
		if self.user.is_staff:
			if not hasattr(self, '_info'):
				self._info = Admin(self)
				
			return self._info
		else:
			return self.info_object
			
	@info.setter
	def info(self, obj):
		if self.user.is_staff:
			return
		self.info_object = obj
	
class Account(models.Model):
	
	profile_object = generic.GenericRelation(
			'UserProfile',
			content_type_field = 'info_type',
			object_id_field = 'info_object_id'
	)
	display_name = models.CharField(max_length = 255, default = '', blank = True)
	assets = fields.DecimalField()
	
	@property
	def account_type(self):
		return self.__class__.__name__.lower()
	
	@property
	def profile(self):
		if not hasattr(self, '_profile'):
			try:
				self._profile = self.profile_object.all()[0]
			except:
				self._profile = None
		
		return self._profile
	
	class Meta:
		abstract = True
		ordering = ['display_name']
		
class Admin(object):

	display_name = u'管理员'
	account_type = u'admin'
	
	def __init__(self, profile):
		self.profile = profile
		
	def update(self, *args, **kwargs):
		return
		
	def save(self, *args, **kwargs):
		return
		
class Person(Account, HasReportModel):

	report_field = 'consumption_reports'

	fixed_assets = fields.DecimalField()
	debt_file = models.ForeignKey(PrivateFile, related_name = 'person_in_debt', null = True, blank = True)
	consumption_reports = models.ManyToManyField(PrivateFile, related_name = 'person_owned_reports')

	company_type = models.ForeignKey(ContentType, null = True, blank = True)
	company_object_id = models.PositiveIntegerField(null = True, blank = True)
	company = generic.GenericForeignKey('company_type', 'company_object_id')
		
	class Meta(Account.Meta):
		pass
	
class Enterprise(Account):
	
	description = models.TextField(blank = True, default = '')
	phone_number = models.CharField(blank = True, max_length = 11, default = '')
	
	members = generic.GenericRelation(
			'Person',
			content_type_field = 'company_type',
			object_id_field = 'company_object_id',
	)

	class Meta(Account.Meta):
		abstract = True
	
class Company(Enterprise, HasReportModel):
	
	report_field = 'financial_reports'
	
	financial_reports = models.ManyToManyField(PrivateFile, related_name = 'company_owned_reports')
	
	class Meta(Enterprise.Meta):
		pass
		
class FinancialInstitution(Enterprise):
	
	BANK = 'BK'
	FUND_COMPANY = 'FC'
	
	INSTITUTION_TYPE_CHOICES = (
			(BANK, 'bank'),
			(FUND_COMPANY, 'fund_company'),
	)
	
	type = models.CharField(max_length = 2, default = BANK, choices = INSTITUTION_TYPE_CHOICES)
	
	class Meta(Enterprise.Meta):
		pass
		
class Bank(FinancialInstitution):

	objects = managers.BankManager()

	class Meta(FinancialInstitution.Meta):
		proxy = True
		
class FundCompany(FinancialInstitution):

	objects = managers.FundCompanyManager()
	
	class Meta(FinancialInstitution.Meta):
		proxy = True