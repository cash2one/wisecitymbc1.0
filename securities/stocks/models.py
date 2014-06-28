#encoding=utf8
from __future__ import division
from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common.fields import DecimalField
from common.mixins import get_inc_dec_mixin
from exceptions import SharesNotEnough
from signals import application_updated

from decimal import Decimal

from notifications import Dispatcher

dispatcher = Dispatcher(u'系统处理了你的股票${type}申请：成功${type}了${stock}。')

class Stock(models.Model):
	
	display_name = models.CharField(max_length = 255, default = '', editable = False)
	
	publisher_type = models.ForeignKey(ContentType, null = True, blank = True)
	publisher_object_id = models.PositiveIntegerField(null = True, blank = True)
	publisher = generic.GenericForeignKey('publisher_type', 'publisher_object_id')
	
	current_price = DecimalField()
	total_shares = models.IntegerField(blank = True, default = 0)
	created_time = models.DateTimeField(auto_now_add = True)
	
	def transfer(self, app_seller, app_buyer, shares):
		seller = app_seller.applicant
		buyer = app_buyer.applicant
		price = app_seller.price
		shares = Decimal(shares)
		app_seller.dec_shares(shares)
		app_buyer.dec_shares(shares)
		print """
			Seller: %s
			Buyer: %s
			Price: %f
			shares: %f""" %(seller, buyer, price, shares)
		money = Decimal(price) * shares
		seller.inc_assets(money)
		buyer.dec_assets(money)
		
		seller.get_stock_share(self, create = True).dec_shares(shares)
		share = buyer.get_stock_share(self, create = True).inc_shares(shares)
		
	def update_price(self, price):
		if Decimal(price) - Decimal(self.current_price) > 1e-4:
			Log.objects.create(stock = self, price = price)
			self.current_price = price
			self.save()
	
	def __unicode__(self):
		return u"股票 %s" % self.display_name
		
	def get_absolute_url(self):
		return '/stocks/detail/?uid=%d' % self.id
	
	class Meta:
		ordering = ['-current_price', '-created_time']
		permissions = (
			('has_stock', 'Has Stock'),
			('own_stock', 'Own stock'),
		)
	
class Log(models.Model):
	
	stock = models.ForeignKey(Stock, related_name = 'logs')
	price = DecimalField()
	created_time = models.DateTimeField(auto_now_add = True)
	
	class Meta:
		ordering = ['-created_time']

class ApplicationManager(models.Manager):

	def fetch_suitable_applications(self, application):
		return self.filter(stock = application.stock, price = application.price, shares__gt = Decimal(0)).exclude(command = application.command)
		
class Application(get_inc_dec_mixin(['shares', 'price'])):

	SELL = 'sell'
	BUY  = 'buy'
	COMMAND_CHOICE = (
		(SELL, u'卖出'),
		(BUY,  u'买入'),
	)

	applicant_type = models.ForeignKey(ContentType, null = True, blank = True)
	applicant_object_id = models.PositiveIntegerField(null = True, blank = True)
	applicant = generic.GenericForeignKey('applicant_type', 'applicant_object_id')
	
	stock = models.ForeignKey(Stock, related_name = 'applications')
	command = models.CharField(max_length = 4, choices = COMMAND_CHOICE)
	price  = DecimalField()
	shares = models.IntegerField(blank = True, default = 0)
	created_time = models.DateTimeField(auto_now_add = True)
	
	# def decrease_or_delete(self, shares):
		# self.dec_shares(shares, commit = False)
		# if self.shares == Decimal(0) and self.id:
			# self.delete()
		# else:
			# self.save()
	
	def get_share(self):
		if not hasattr(self, '_share'):
			self._share = self.applicant.get_stock_share(stock = self.stock)
			
		return self._share
	
	def clean(self):
	#	current_price, new_price = Decimal(self.stock.current_price), Decimal(self.price)
		#assert abs((current_price-new_price) / current_price) <= 0.2, "Stock price overflow."
		#if self.command and self.command == self.BUY:
		#	self.applicant.check_assets(new_price * self.shares)

		#if self.command and self.command == self.SELL:
		#	self.get_share()
		#	if self._share is None or self._share.shares < self.shares:
		#		raise SharesNotEnough		
		pass
	
	def save(self, send = False, *args, **kwargs):
		if send and self.id is not None:
			application_updated.send(self, application = self)
		
		super(Application, self).save(*args, **kwargs)
	
	def __unicode__(self):
		if self.command == self.SELL:
			action = u'卖出'
		else:
			action = u'买入'
			
		return u'股票 %s 的%s申请' % (self.stock.display_name, action) 
	
	class Meta:
		ordering = ['-created_time', 'price']
		
	objects = ApplicationManager()
		
class ShareManager(models.Manager):				
			
	pass
		
class Share(get_inc_dec_mixin(['shares'])):
	
	owner_type = models.ForeignKey(ContentType, null = True, blank = True, related_name = 'stock_shares')
	owner_object_id = models.PositiveIntegerField(null = True, blank = True)
	owner = generic.GenericForeignKey('owner_type', 'owner_object_id')
	
	stock = models.ForeignKey(Stock, related_name = 'shares')
	shares = models.IntegerField(blank = True, default = 0)
	
	objects = ShareManager()
	
def process_application_updated(sender, **kwargs):
	
	def get_type(app):
		if app.command == Application.SELL:
			return u'卖出'
		else:
			return u'买入'	
	
	application = kwargs.get('application', None)
	stock = application.stock
	price = application.price
	
	application_sets = []
	quantity = application.shares
	for _application in Application.objects.fetch_suitable_applications(application).prefetch_related():
		application_sets.append((_application, min(_application.shares, quantity)))
		quantity -= _application.shares
		if quantity <= 0:
			break
	if not application_sets:
		return

	notifications = [{
			'recipient': application.applicant.profile.user,
			'target': application,
			'action': 'delete',
			'args': {
				'type': get_type(application),
				'stock': stock
			}
	}]
		
	for _application, share in application_sets:
		if application.command == Application.BUY:
			seller, buyer = _application, application
		else:
			seller, buyer = application, _application
		notifications.append({
				'recipient': _application.applicant.profile.user,
				'target': _application,
				'action': 'delete',
				'args': {
					'type': get_type(_application),
					'stock': stock
				}
		})
		stock.transfer(seller, buyer, share)	
		
	if quantity < 0:
		notifications[-1]['action'] = 'null'
	elif quantity > 0:
		notifications[0]['action'] = 'null'
	dispatcher.multi_send('_', data = notifications)
		
	stock.update_price(price)
	
application_updated.connect(process_application_updated)
