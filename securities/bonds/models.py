#encoding=utf8
from django.db import models
from django.db.models import F

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common.fields import DecimalField, TimeDeltaField
from common.mixins import get_inc_dec_mixin
from exceptions import BondPublished

from decimal import Decimal
from django.db import connection

from django.core.exceptions import ValidationError
from django.conf import settings
from notifications import Dispatcher

dispatcher = Dispatcher({
		'start': u'${bond}成功发布。',
		'end': u'${bond}已经结束。'
})

class BondManager(models.Manager):
	
	def published(self):
		return self.filter(published = True)

class Bond(models.Model):
	
	GOVERNMENT = 'GOV'
	ENTERPRISE = 'ENT'
	TYPE_CHOICE = (
			(GOVERNMENT, 'Government'),
			(ENTERPRISE, 'Enterprise'),
	)
	
	display_name = models.CharField(max_length = 255, default = '', blank = True, verbose_name = u'名称')
	
	publisher_type = models.ForeignKey(ContentType, null = True, blank = True)
	publisher_object_id = models.PositiveIntegerField(null = True, blank = True)
	publisher = generic.GenericForeignKey('publisher_type', 'publisher_object_id')
	type = models.CharField(max_length = 3, choices = TYPE_CHOICE)
	
	published = models.BooleanField(default = False)
	
	profit_rate = DecimalField()
	max_money = DecimalField(default = 0)
	lasted_time = TimeDeltaField()
	published_time = models.DateTimeField()
	created_time = models.DateTimeField(auto_now_add = True)
	
	def __init__(self, *args, **kwargs):
		self.__total_money = None
		return super(Bond, self).__init__(*args, **kwargs)
	
	def __unicode__(self):
		if self.type == self.GOVERNMENT:
			_type = u'政府'
		else:
			_type = u'公司'
			
		return u'%s债券 %s' % (_type, self.display_name)
	
	def get_absolute_url(self):
		return '/bonds/detail/?uid=%d' % self.id
	
	def send_notification(self, key):
		return dispatcher.send(key, {'bond': self}, recipient = self.publisher.profile.user, target = self)
	
	def publish(self):
		self.published = True
		self.save()
		self.send_notification('start')
		
	def check_published(self):
		if self.published:
			raise BondPublished
	
	def finish(self, times = 1):
		rate = self.profit_rate / 100
		total = Decimal(0)
		shares = self.shares.prefetch_related()
		for share in shares:
			money = share.money * ((1+rate) ** times)
			total += money
			share.owner.inc_assets(money)
		if self.type == self.ENTERPRISE:
			self.publisher.dec_assets(total)
		self.send_notification('end')
		shares.delete()
		self.delete()
	
	def ransom(self):
		if not self.published:
			raise ValidationError("The bond hasn't been published.")
		times = self.lasted_time // (5*60)+1
		self.finish(times)
	
	def share_profits(self):
		rate = self.profit_rate / 100
		total = Decimal(0)
		for share in self.shares.prefetch_related():
			money = share.money * rate
			total += money
			share.owner.inc_assets(money)
		if self.type == self.ENTERPRISE:
			self.publisher.dec_assets(total)
	
	def clean_fields(self, *args, **kwargs):
		if not self.type:
			self.type = self.GOVERNMENT if self.publisher.__class__.__name__ == 'Government' else self.ENTERPRISE
			
		super(Bond, self).clean_fields(*args, **kwargs)
	
	def apply_money(self, actor, money):
		share = actor.get_bond_share(self, create = True, money = money).inc_money(money)
		self.publisher.inc_assets(money)
	
	@property
	def total_money(self):
		if self.__total_money is None:
			self.__total_money = Share.objects.get_total_money(self)
			
		return self.__total_money
		
	class Meta:
		ordering = ['-created_time']
		verbose_name = u'债券'
		verbose_name_plural = u'债券'
		permissions = (
			('has_bond', 'Has bond'),
			('own_bond', 'Own bond'),
		)
		
	objects = BondManager()
	
class ShareManager(models.Manager):

	def get_total_money(self, bond):
		cursor = connection.cursor()
		sql = "SELECT SUM(money) FROM bonds_share GROUP BY bond_id HAVING bond_id=%d" % bond.id
		cursor.execute(sql)
		result = cursor.fetchone()
		print result
		if result:
			return result[0]
		else:
			return 0
	
class Share(get_inc_dec_mixin(['money'])):
	
	owner_type = models.ForeignKey(ContentType, null = True, blank = True, related_name = 'bond_shares')
	owner_object_id = models.PositiveIntegerField(null = True, blank = True)
	owner = generic.GenericForeignKey('owner_type', 'owner_object_id')
	
	bond = models.ForeignKey(Bond, related_name = 'shares')
	money = DecimalField()
	
	objects = ShareManager()
	
	class Meta:
		ordering = ['-money']
