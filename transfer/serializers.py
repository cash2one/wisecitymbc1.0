#encoding=utf8
from rest_framework import serializers
from .models import TransferLog, Deposit
from accounts.serializers import BankSerializer, AccountField
from decimal import Decimal

class TransferSerializer(serializers.Serializer):
	
	to = AccountField()
	money = serializers.DecimalField()

	def __init__(self, actor, *args, **kwargs):
		self.actor = actor
		return super(TransferSerializer, self).__init__(*args, **kwargs)

	def validate_money(self, attrs, source):
		if not self.actor.check_assets(attrs[source]*Decimal(1.001)):
			raise serializers.ValidationError(u"账户余额不足（注意有手续费）。")
			
		return attrs

	def restore_object(self, attrs, instance = None):
		return TransferLogSerializer(self.actor.transfer_money(attrs['to'], attrs['money'])).data
		
class StoreSerializer(serializers.Serializer):
	
	money = serializers.DecimalField()
	
	def __init__(self, actor, bank, command, *args, **kwargs):
		self.actor = actor
		self.bank = bank
		self.command = command
		return super(StoreSerializer, self).__init__(*args, **kwargs)
		
	def validate_money(self, attrs, source):
		money = attrs[source]
		if self.command == 'store' and not self.actor.check_assets(money):
			raise serializers.ValidationError(u"账户余额不足。")
		if self.command == 'remove':
			try:
				deposit = self.actor.deposits.get(bank = self.bank)
				if deposit.money < money:
					raise serializers.ValidationError(u"银行账户余额不足。")
			except Deposit.DoesNotExist:
				raise serializers.ValidationError(u"银行账户余额不足。")
				
		return attrs
		
	def restore_object(self, attrs, instance = None):
		if self.command == 'store':
			obj = self.actor.store_money(self.bank, attrs['money'])
		else:
			obj = self.actor.remove_money(self.bank, attrs['money'])
			
		return DepositSerializer(obj).data
		
class TransferLogSerializer(serializers.ModelSerializer):
	
	transfer_by = AccountField(fields = ['account_type','display_name','url'])
	transfer_to = AccountField(fields = ['account_type','display_name','url'])	
	
	class Meta:
		model = TransferLog
		fields = ('transfer_by', 'transfer_to', 'money', 'created_time')

class DepositSerializer(serializers.ModelSerializer):

	bank = BankSerializer(exclude = ['members', 'assets'])

	class Meta:
		model = Deposit
		fields = ('bank', 'money')
