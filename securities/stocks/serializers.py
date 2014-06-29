#encoding=utf8
from __future__ import division
from rest_framework import serializers, pagination
from .models import Stock, Share, Application, Log
from rest_framework.serializers import ValidationError
from accounts.serializers import AccountField
import mixins

class CreateStockSerializer(serializers.Serializer):

	owner = AccountField()
	proxy = AccountField()
	current_price = serializers.DecimalField()
	total_shares = serializers.IntegerField()
	display_name = serializers.CharField()
	
	def validate_owner(self, attrs, source):
		owner = attrs[source]
		if not isinstance(owner, mixins.OwnStockMixin):
			raise serializers.ValidationError(u"用户%s没有股票发布权限。" % owner)
			
		return attrs
		
	def validate_proxy(self, attrs, source):
		proxy = attrs[source]
		if not isinstance(proxy, mixins.HasStockMixin):
			raise serializers.ValidationError(u"用户%s没有股票买卖权限。" % proxy)
			
		return attrs
		
	def restore_object(self, attrs, instance = None):
		owner, proxy = attrs.pop('owner'), attrs.pop('proxy')
		stock = Stock.objects.create(publisher = owner, **attrs)
		share = Share.objects.create(stock = stock, owner = proxy, shares = attrs['total_shares'])
		
		return stock

class StockSerializer(serializers.ModelSerializer):

	publisher = AccountField(read_only = True, exclude = ['members'])
	url = serializers.SerializerMethodField("get_url")
	
	def get_url(self, obj):
		return "/stocks/detail/?uid=%d" % obj.id
		
	class Meta:
		model = Stock
		exclude = ('publisher_type', 'publisher_object_id')
		
class LogSerializer(serializers.ModelSerializer):

	class Meta:
		model = Log
		fields = ('created_time', 'price')
		
class ShareSerializer(serializers.ModelSerializer):
	
	stock = StockSerializer(fields = ('display_name', 'id', 'current_price', 'url'))
	
	class Meta:
		model = Share
		exclude = ('owner_type', 'owner_object_id', 'owner')
		
class ApplicationSerializer(serializers.ModelSerializer):
	
	stock = StockSerializer(fields = ['id', 'display_name'])
	
	def __init__(self, *args, **kwargs):
		res = super(ApplicationSerializer, self).__init__(*args, **kwargs)
		if self.object and self.many == False:
			self.__stock = self.object.stock
			self.__type = self.object.command
			self.__actor = self.object.applicant
			
		return res
		
	def validate_price(self, attrs, source):
		price = self.__stock.current_price
		if abs((price-attrs[source]) / price) >= 0.2:
			raise ValidationError(u"申请的股价不能高出/低于现价的20%。")
			
		if self.__type == Application.BUY and not self.__actor.check_assets(attrs[source] * attrs['shares']):
			raise ValidationError(u"账户余额不足。")
			
		return attrs
		
	def validate_shares(self, attrs, source):
		
		def raise_error():
			raise ValidationError(u"你所持有的股份数不够。")
			
		if self.__type == Application.BUY:
			return attrs
		try:
			share = self.__actor.stock_shares.get(stock = self.__stock)
			if share.shares < attrs['shares']:
				raise_error()
		except Share.DoesNotExist:
			raise_error()
			
		return attrs
	
	class Meta:
		model = Application
		exclude = ('applicant_type', 'applicant_object_id', 'applicant', 'command',)

class ApplySerializer(serializers.Serializer):
	
	shares = serializers.IntegerField()
	price = serializers.DecimalField()
	
	def __init__(self, type, stock, actor, *args, **kwargs):
		self.__stock = stock
		self.__type = type
		self.__actor = actor
		return super(ApplySerializer, self).__init__(*args, **kwargs)
		
	def validate_price(self, attrs, source):
		price = self.__stock.current_price
		if abs((price-attrs[source]) / price) >= 0.2:
			raise ValidationError(u"申请的股价不能高出/低于现价的20%。")
			
		if self.__type == Application.BUY and not self.__actor.check_assets(attrs[source] * attrs['shares']):
			raise ValidationError(u"账户余额不足。")
			
		return attrs
		
	def validate_shares(self, attrs, source):
		
		def raise_error():
			raise ValidationError(u"你所持有的股份数不够。")
			
		if self.__type == Application.BUY:
			return attrs
		try:
			share = self.__actor.stock_shares.get(stock = self.__stock)
			if share.shares < attrs['shares']:
				raise_error()
		except Share.DoesNotExist:
			raise_error()
			
		return attrs
		
	def restore_object(self, attrs, instance = None):
		return self.__actor._apply(self.__type, self.__stock, attrs['price'], attrs['shares'])
