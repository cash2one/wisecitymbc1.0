from rest_framework import serializers, pagination
from .models import Stock, Share, Application, Log
from accounts.serializers import AccountField

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
	
	stock = serializers.Field(source = 'stock.display_name')
	
	class Meta:
		model = Share
		exclude = ('owner_type', 'owner_object_id', 'owner')
		
class ApplicationSerializer(serializers.ModelSerializer):
	
	stock = StockSerializer(fields = ['id', 'display_name'])
	
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
		super(ApplySerializer, self).__init__(*args, **kwargs)
		
	def restore_object(self, attrs, instance = None):
		return self.__actor._apply(self.__type, self.__stock, attrs['price'], attrs['shares'])