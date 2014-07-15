from functools import partial
from django.db import models
from timeline.fields import FinancialYearField
from datetime import timedelta
from rest_framework.fields import WritableField

DecimalField = partial(
		models.DecimalField,
		max_digits = 20,
		decimal_places = 4,
		default = 0
)

class TimeDeltaSerializerField(WritableField):

	def __init__(self, *args, **kwargs):
		kwargs.pop('min_value','')
		super(TimeDeltaSerializerField, self).__init__(*args, **kwargs)

class TimeDeltaField(models.IntegerField):

	descrption = "datetime.timedelta"
	__metaclass__ = models.SubfieldBase
	
	def get_prep_value(self, value):
		if isinstance(value, timedelta):
			return int(value.total_seconds())
		if isinstance(value, (str, unicode)):
			h,m = map(int, value.split(':'))
			return h*3600+m*60
			
		return super(TimeDeltaField, self).get_prep_value(value)
		
	def from_native(self, value):
		if isinstance(value, (str, unicode)):
			h,m = map(int, value.split(':'))
			return h*3600+m*60
		else:
			return value
		
	def to_python(self, value):
		if isinstance(value, (str, unicode)):
			h,m = map(int, value.split(':'))
			value =  h*3600+m*60
		val = value / 60
		return "%.2d:%.2d" % (val // 60, val % 60)
		return value
