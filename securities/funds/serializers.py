#encoding=utf8
from rest_framework import serializers
from .models import Fund, Share
from accounts.serializers import AccountField
from django.contrib.auth.models import User

class FundSerializer(serializers.ModelSerializer):

	publisher = AccountField(read_only = True)
	total_money = serializers.SerializerMethodField("get_total_money")
	url = serializers.Field(source = 'get_absolute_url')
	
	def get_total_money(self, obj):
		return Share.objects.get_total_money(obj)

	class Meta:
		exclude = ('publisher_type', 'publisher_object_id','account', )
		model = Fund
		
class CreateAccountSerializer(serializers.Serializer):		

	username = serializers.CharField()
	password = serializers.CharField()
	
	def validate_username(self, attrs, source):
		if User.objects.filter(username = attrs[source]).exists():
			raise serializers.ValidationError(u"用户名已存在。")
			
		return attrs
		
	def restore_object(self, attrs, instance = None):
		return self.fund.create_user(**attrs)
		
	def __init__(self, fund, *args, **kwargs):
		self.fund = fund
		return super(CreateAccountSerializer, self).__init__(*args, **kwargs)
		
class ShareSerializer(serializers.ModelSerializer):
	
	fund = FundSerializer(exclude = ['publisher'])
	
	class Meta:
		exclude = ('owner_type', 'owner_object_id', 'owner')
		model = Share
		
class ApplySerializer(serializers.Serializer):
	
	money = serializers.DecimalField()
	
	def __init__(self, actor, fund, command, *args, **kwargs):
		self.actor = actor
		self.fund = fund
		self.command = command
		return super(ApplySerializer, self).__init__(*args, **kwargs)
		
	def validate_money(self, attrs, source):
		money = attrs[source]
		if self.command == 'buy' and not self.actor.check_assets(money):
			raise serializers.ValidationError(u"账户余额不足。")
		if self.command == 'ransom':
			share = self.actor.get_fund_share(self.fund)
			if not share or share.money < money:
				raise serializers.ValidationError(u"你没有投入足够的资金。")
		
		return attrs
		
	def restore_object(self, attrs, instance = None):
		self.money = attrs['money']
		if self.command == 'buy':
			self.actor.buy_fund(self.fund, self.money)
		else:
			self.actor.ransom_fund_share(self.fund, self.money)
		return {}
