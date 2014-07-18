#encoding=utf8
from rest_framework import serializers
from .models import Bond, Share
from accounts.serializers import AccountField

class BondSerializer(serializers.ModelSerializer):

	publisher = AccountField()
	url = serializers.Field(source = 'get_absolute_url')

	class Meta:
		exclude = ('publisher_type', 'publisher_object_id','account', 'type')
		model = Bond
		
class ShareSerializer(serializers.ModelSerializer):
	
	bond = BondSerializer(exclude = ['publisher'])
	
	class Meta:
		exclude = ('owner_type', 'owner_object_id', 'owner')
		model = Share
		
class ApplySerializer(serializers.Serializer):
	
	money = serializers.DecimalField()
	
	def __init__(self, actor, bond, *args, **kwargs):
		self.actor = actor
		self.bond = bond
		return super(ApplySerializer, self).__init__(*args, **kwargs)
		
	def validate_money(self, attrs, source):
		money = attrs[source]
		if self.bond.total_money+money > self.bond.max_money:
			raise serializers.ValidationError(u"债券剩余数额不足，请调整购买金额。")
		
		if not self.actor.check_assets(money):
			raise serializers.ValidationError(u"账户余额不足。")
		
		return attrs
		
	def restore_object(self, attrs, instance = None):
		self.money = attrs['money']
		self.actor.buy_bond(self.bond, self.money)
		return {}
