#encoding=utf8
from common.mixins import *
from models import Share, RansomApplication, dispatcher
from django.core.exceptions import ValidationError

__all__ = ['OwnFundMixin', 'HasFundMixin']

class HasFundMixin(models.Model):
	
	permission = 'has_fund'
	
	fund_shares = generic.GenericRelation(
			'funds.Share',
			content_type_field = 'owner_type',
			object_id_field = 'owner_object_id',
	)

	def ransom_fund_share(self, fund, money):
		application = RansomApplication(
				fund = fund,
				money = money,
				owner = self
		)
		application.save()
		dispatcher.send('ransom', {
				'actor': self,
				'money': money,
		}, recipient = fund.account.profile.user, action = 'delete', important = True)

	def get_fund_share(self, fund, create = False, **kwargs):
		try:
			return self.fund_shares.get(fund = fund)
		except Share.DoesNotExist:
			if create:
				return Share(owner = self, fund = fund, **kwargs)
	
	def buy_fund(self, fund, money):
		fund.apply_money(self, money)
		self.dec_assets(money)
		
	class Meta:
		abstract = True

class OwnFundMixin(models.Model):
	
	permission = 'own_fund'
	
	funds = generic.GenericRelation(
			'funds.Fund',
			content_type_field = 'publisher_type',
			object_id_field = 'publisher_object_id'
	)	
	
	class Meta:
		abstract = True
