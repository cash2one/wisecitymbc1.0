#encoding=utf8
from .models import TransferLog, Deposit
from common.mixins import *
from decimal import Decimal
from notifications import Dispatcher

__all__ = ['CanStoreMixin', 'CanTransferMixin']

dispatcher = Dispatcher(u'${from}转帐了￥${money}给你。')

class CanStoreMixin(models.Model):
	
	permission = 'can_store'
	
	deposits = generic.GenericRelation(
			'transfer.Deposit',
			content_type_field = 'owner_content_type',
			object_id_field = 'owner_object_id',
	)
	
	def store_money(self, bank, money):
		self.dec_assets(money)
		bank.inc_assets(money)
		try:
			deposit = self.deposits.get(bank = bank)
			deposit.inc_money(money)
			return deposit
		except Deposit.DoesNotExist:
			return Deposit.objects.create(
					bank = bank,
					owner = self,
					money = money
			)
			
	def remove_money(self, bank, money):
		try:
			deposit = self.deposits.get(bank = bank)
			deposit.dec_money(money)
			self.inc_assets(money)
			bank.dec_assets(money)
			return deposit
		except Deposit.DoesNotExist:
			raise Exception, "Deposits not enough."
			
	class Meta:
		abstract = True
		
class CanTransferMixin(models.Model):
	
	permission = 'can_transfer'
	
	transfer_logs = generic.GenericRelation(
			'transfer.TransferLog',
			content_type_field = 'transfer_by_content_type',
			object_id_field = 'transfer_by_object_id',
			related_name = 'transfer_by_%(class)s',
	)	
	
	receive_logs = generic.GenericRelation(
			'transfer.TransferLog',
			content_type_field = 'transfer_to_content_type',
			object_id_field = 'transfer_to_object_id',
	)	
	
	def transfer_money(self, transfer_to, money):
		money = Decimal(money)
		dec_money = money * Decimal(1.001)
		self.dec_assets(dec_money)
		transfer_to.inc_assets(money)
		dispatcher.send(
			'_',
			recipient = transfer_to.profile.user,
			args = {
				'money': money,
				'from': self
			}
		)
		return TransferLog.objects.create(
				transfer_to = transfer_to,
				transfer_by = self,
				money = money
		)
		
	class Meta:
		abstract = True
