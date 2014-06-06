#encoding=utf8
from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from common.fields import DecimalField, TimeDeltaField
from common.mixins import get_inc_dec_mixin

from django.db import connection

from decimal import Decimal

class FundManager(models.Manager):
	
	def published(self):
		return self.filter(published = True)

class Fund(models.Model):

	OPEN = 'open'
	CLOSE = 'close'
	TYPE_CHOICE = (
		(OPEN, 'open'),
		(CLOSE, 'close'),
	)
	
	display_name = models.CharField(max_length = 255, default = '')

	publisher_type = models.ForeignKey(ContentType, null = True, blank = True)
	publisher_object_id = models.PositiveIntegerField(null = True, blank = True)
	publisher = generic.GenericForeignKey('publisher_type', 'publisher_object_id')
	
	account = models.OneToOneField('accounts.Fund', related_name = 'fund', null = True, blank = True)
	
	published = models.BooleanField(default = False)
	
	min_return_rate = DecimalField()
	return_rate = DecimalField()
	max_return_rate = DecimalField()
	initial_money = DecimalField()
	lasted_time = TimeDeltaField()
	published_time = models.DateTimeField()
	
	fund_type = models.CharField(max_length = 10, choices = TYPE_CHOICE)
	
	created_time = models.DateTimeField(auto_now_add = True)
	
	def __unicode__(self):
		if self.fund_type == self.OPEN:
			_type = u'开放'
		else:
			_type = u'封闭'
		return u'%s式基金 %s' % (_type, self.display_name)
	
	def __init__(self, *args, **kwargs):
		self.__total_money = None
		return super(Fund, self).__init__(*args, **kwargs)
	
	def apply_money(self, actor, money):
		share = actor.get_fund_share(self, create = True, money = money)
		if share.id is None:
			share.save()
		else:
			share.inc_money(money)
		if self.published:
			self.account.inc_assets(money)
		
	def share_profits(self, commit = True):
		rate = self.return_rate / 100
		cursor = connection.cursor()
		cursor.execute(
				"UPDATE funds_share SET money=ROUND(money*(1+%s), 4) WHERE fund_id=%d" % (rate, self.id)
		)
		if commit:
			connection.connection.commit()
	
	def _end(self):
		if self.account:
			self.account.profile.user.delete()
			self.account.delete()
		self.delete()
	
	def finish(self):
		shares = self.shares.prefetch_related()
		for share in self.shares.all():
			share.owner.inc_assets(share.money)
		shares.delete()
		self._end()
	
	def publish(self, delete_on_failed = True, username = 'fundd', password = None):
		try:
			print self.total_money
			assert self.total_money >= self.initial_money
		except AssertionError:
			if delete_on_failed:
				self._end()
			else:
				raise
				
		User = ContentType.objects.get(app_label = 'auth', model = 'user').model_class()
		user = User.objects.create_user(username = username, password = password or User.objects.make_random_password(6))
		account = user.profile.create_info('Fund', display_name = self.display_name, assets = self.total_money)
		self.account = account
		self.published = True
		self.save()
		return user
	
	def can_buy(self):
		return not (not self.published and self.fund_type == self.CLOSE)
	
	@property
	def total_money(self):
		if self.__total_money is None:
			self.__total_money = Share.objects.get_total_money(self)
			
		return self.__total_money
	
	class Meta:
		ordering = ['-created_time']
		
	objects = FundManager()
		
class ShareManager(models.Manager):
	
	def get_total_money(self, fund):
		cursor = connection.cursor()
		sql = "SELECT SUM(money) FROM funds_share GROUP BY fund_id HAVING fund_id=%d" % fund.id
		cursor.execute(sql)
		result = cursor.fetchone()
		print result
		if result:
			return result[0]
		else:
			return 0
		
class Share(get_inc_dec_mixin(['money'])):

	owner_type = models.ForeignKey(ContentType, null = True, blank = True, related_name = 'fund_shares')
	owner_object_id = models.PositiveIntegerField(null = True, blank = True)
	owner = generic.GenericForeignKey('owner_type', 'owner_object_id')
	
	fund = models.ForeignKey(Fund, related_name = 'shares')
	money = DecimalField()
	percentage = DecimalField()
	
	def save(self, *args, **kwargs):
		super(Share, self).save(*args, **kwargs)
		cursor = connection.cursor()
		cursor.execute(
				"""UPDATE funds_share, (SELECT SUM(money) as sum FROM funds_share WHERE fund_id=%d) as t SET percentage=ROUND(money/t.sum*100,4)
				""" % self.fund.id
		)
	
	def pre_set_money(self, value):
		total_money = self.fund.total_money
		new_total_money = total_money + value
		cursor = connection.cursor()
		ctx = {
			'total': total_money,
			'new_total': new_total_money,
			'id': self.id,
			'fund_id': self.fund.id,
			'value': value,
		}

		if self.fund.published:
			cursor.execute(
					"""UPDATE funds_share SET percentage=CASE id WHEN %(id)d THEN ROUND((percentage/100*%(total)d+%(value)s)/%(new_total)s*100, 4)
						ELSE ROUND(percentage*%(total)s/%(new_total)s, 4) END WHERE fund_id=%(fund_id)d
					""" % ctx
			)
		else:
			cursor.execute(
					"""UPDATE funds_share SET percentage=CASE id WHEN %(id)d THEN ROUND((money+%(value)s)/%(new_total)s*100,4) ELSE ROUND(money/%(new_total)s*100, 4) END
					   WHERE fund_id=%(fund_id)d
					""" % ctx
			)
			
	
	objects = ShareManager()
	
	class Meta:
		ordering = ['-money']
