from common.mixins import *
from models import Share, Application
from signals import application_updated

__all__ = ['HasStockMixin', 'OwnStockMixin']

class OwnStockMixin(models.Model):
	
	permission = 'own_stock'
	
	stocks = generic.GenericRelation(
			'stocks.Stock',
			content_type_field = 'publisher_type',
			object_id_field = 'publisher_object_id'
	)	
	
	class Meta:
		abstract = True

class HasStockMixin(models.Model):

	permission = 'has_stock'

	stock_shares = generic.GenericRelation(
			'stocks.Share',
			content_type_field = 'owner_type',
			object_id_field = 'owner_object_id'
	)
	
	_stock_applications = generic.GenericRelation(
			'stocks.Application',
			content_type_field = 'applicant_type',
			object_id_field = 'applicant_object_id'
	)
	
	@property
	def stock_applications(self):
		return self._stock_applications.filter(shares__gt = 0)
	
	def get_stock_share(self, stock, create = False, **kwargs):
		try:
			return self.stock_shares.get(stock = stock)
		except Share.DoesNotExist:
			if create:
				return Share(owner = self, stock = stock, **kwargs)
				
	def _apply(self, command, stock, price, shares):
		application = Application(stock = stock, applicant = self, price = price, command = command, shares = shares)
		application.clean()
		application.save()
		application_updated.send(self, application = application)
		
		return application
		
	def buy_stock(self, stock, price, shares):
		return self._apply(Application.BUY, stock, price, shares)
		
	def sell_stock(self, stock, price, shares):
		return self._apply(Application.SELL, stock, price, shares)
	
	class Meta:
		abstract = True
