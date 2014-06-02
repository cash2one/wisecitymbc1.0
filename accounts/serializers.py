from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
import models
from django.contrib.contenttypes.models import ContentType

from django.http import Http404

from common.serializers import FileField 

def get_industry_serializer(field_name = 'industry'):

	class HasIndustrySerializer(serializers.Serializer):
		
		industry = serializers.Field(source = '%s.display_name' % field_name)
		
	return HasIndustrySerializer

class AccountSerializer(serializers.ModelSerializer):

	account_type = serializers.CharField(read_only = True)
	url = serializers.SerializerMethodField('get_url')
	
	def get_url(self, obj):
		return reverse('user-profile', kwargs = {'pk':obj.profile.user.pk})
		
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
	
class PersonSerializer(PersonalSerializer, get_industry_serializer()):
	
	company = serializers.SerializerMethodField('get_company')
	debt_files = FileField(many = True, required = False)
	consumption_reports = FileField(required = False, many = True)
	
	def get_company(self, obj):
		if obj.company is None:
			return 
		serializer = get_serializer_by_object(obj.company)
		return serializer(obj.company, exclude = [
				'members',
				'financial_reports',
				'assets',
				
		]).data
	
	class Meta:
		model = models.Person	
		exclude = ['company_type', 'company_object_id']
		
class EnterpriseSerializer(AccountSerializer):
	
	members = PersonSerializer(many = True, required = False, exclude=[
			'company',
			'consumption_reports',
			'debt_files',
	])
	financial_reports = FileField(many = True, required = False)
	
	class Meta:
		model = models.Enterprise
		
class CompanySerializer(EnterpriseSerializer, get_industry_serializer()):
	
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

	def get_profile(self, obj):
		profile = obj.profile.info
		if profile is None:
			return {}
		cls_name = '%sSerializer' % profile.__class__.__name__
		a = globals()
		return globals()[cls_name](obj.profile.info).data
		
	class Meta:
		model = User
		fields = ('is_admin', 'username', 'profile', 'id')
		
def get_serializer_by_object(obj):
	return globals()['%sSerializer' % obj.__class__.__name__]
	
class EnterpriseField(serializers.WritableField):
	
	def field_to_native(self, obj, field_name):
		enterprise = getattr(obj, field_name)
		return get_serializer_by_object(enterprise)(enterprise).data
		
	def field_from_native(self, data, files, field_name, into):
		enter_data = data[field_name]
		cls = ContentType.objects.get(app_label = 'accounts', model = enter_data['type'])
		
		if not cls.model_class().objects.filter(pk = enter_data['id']).exists():
			raise Http404
		
		into['%s_type' % field_name] = cls
		into['%s_object_id' % field_name] = enter_data['id']