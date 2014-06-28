#encoding=utf8
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import models
from django.contrib.contenttypes.models import ContentType

from django.http import Http404

from common.serializers import FileField 

class AccountSerializer(serializers.HyperlinkedModelSerializer):

	account_type = serializers.CharField(read_only = True)
	url = serializers.SerializerMethodField('get_url')
	id = serializers.IntegerField(read_only = True)
	
	safe_exclude = ['assets']
	
	def get_url(self, obj):
		return '%s?uid=%d' % (reverse('accounts.profile'), obj.profile.user.id)
		
	class Meta:
		model = models.Account
	
class MediaSerializer(AccountSerializer):
	
	class Meta:
		model = models.Media

class PersonalSerializer(AccountSerializer):

	class Meta:
		model = models.PersonalModel
		
class GovernmentSerializer(PersonalSerializer):
	
	class Meta:
		model = models.Government

class HyperlinkedCompanySerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = models.Company
		fields = ('url', 'display_name')
		lookup_field = 'pk'
	
class PersonSerializer(PersonalSerializer):
	
	company = serializers.SerializerMethodField('get_company')
	debt_files = FileField(many = True, required = False)
	consumption_reports = FileField(required = False, many = True)
	safe_exclude = ['assets', 'debt_files', 'consumption_reports', 'company']
	
	def get_company(self, obj):
		if obj.company is None:
			return 
		serializer = get_serializer_by_object(obj.company)
		return serializer(obj.company, exclude = [
				'members',
				'financial_reports',
				'assets',
		], safe_fields = True).data
	
	class Meta:
		model = models.Person	
		exclude = ['company_type', 'company_object_id']
		
class EnterpriseSerializer(AccountSerializer):
	
	members = PersonSerializer(many = True, required = False, exclude=[
			'company',
			'consumption_reports',
			'debt_files',
	], safe_fields = True)
	financial_reports = FileField(many = True, required = False)
	
	safe_exclude = ['financial_reports', 'assets']
	
	class Meta:
		model = models.Enterprise
		
class CompanySerializer(EnterpriseSerializer):
	
	financial_reports = FileField(many = True, required = False)
	
	class Meta:
		model = models.Company	
		
class BankSerializer(EnterpriseSerializer):
	
	class Meta:
		model = models.Bank
		
class FundCompanySerializer(EnterpriseSerializer):
	
	class Meta:
		model = models.FundCompany
		
class FundSerializer(AccountSerializer):

	class Meta:
		model = models.Fund

class UserSerializer(serializers.ModelSerializer):

	is_admin = serializers.Field(source = 'is_staff')
	profile  = serializers.SerializerMethodField('get_profile')
	url = serializers.SerializerMethodField('get_url')
	
	def get_url(self, obj):
		return '%s?uid=%d' % (reverse('accounts.profile'), obj.id)

	def get_profile(self, obj):
		profile = obj.profile.info
		if profile is None:
			return {}
		cls_name = '%sSerializer' % profile.__class__.__name__
		return globals()[cls_name](obj.profile.info, safe_fields = self.safe_fields).data
		
	class Meta:
		model = User
		fields = ('is_admin', 'username', 'profile', 'id', 'url')
		
def get_serializer_by_object(obj):
	return get_serializer_by_class(obj.__class__)
	
def get_serializer_by_class(cls):
	return globals()['%sSerializer' % cls.__name__]
	
def get_enterprises():
	res = []
	for cls in (models.Company, models.FundCompany, models.Bank):
		serializer = get_serializer_by_class(cls)
		res.extend(serializer(cls.objects.all(), many = True).data)
		
	return res
	
class AccountField(serializers.WritableField):
	
	def __init__(self, *args, **kwargs):
		self.exclude = kwargs.pop('exclude',[])
		self.fields = kwargs.pop('fields', [])
		return super(AccountField, self).__init__(*args, **kwargs)
	
	def field_to_native(self, obj, field_name):
		enterprise = getattr(obj, field_name)
		return get_serializer_by_object(enterprise)(
				enterprise, 
				safe_fields = True, 
				exclude = self.exclude,
				fields = self.fields
		).data
		
	def field_from_native(self, data, files, field_name, into):
		if not self.required:
			return False
		enter_data = data[field_name]
		if isinstance(enter_data, (str, unicode)):
			data = models.filter_accounts(display_name = enter_data)
			if not data:
				raise ValidationError("account")
				into[field_name] = None
				return None
			else:
				data = data[0]
				enter_data = {'type': data['account_type'], 'id': data['id']}
		cls = ContentType.objects.get(app_label = 'accounts', model = enter_data['type'])
		
		try:
			obj = cls.model_class().objects.get(pk = enter_data['id'])
		except cls.model_class().DoesNotExist:
			raise Http404
		
		into['%s_type' % field_name] = cls
		into['%s_object_id' % field_name] = enter_data['id']
		into[field_name] = obj
		
		return obj
