#encoding=utf8
from django.db import models

from common.fields import DecimalField

class Future(models.Model):
	display_name = models.CharField(max_length = 30, default = '', verbose_name=u'名称')
	current_price = DecimalField(verbose_name = u'价格')
	
	def __unicode__(self):
		return self.display_name
	
	class Meta:
		verbose_name = u'期货'
		verbose_name_plural = u'期货'