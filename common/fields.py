from functools import partial
from django.db import models
from timeline.fields import FinancialYearField
from datetime import timedelta

DecimalField = partial(
		models.DecimalField,
		max_digits = 15,
		decimal_places = 4,
		default = 0
)

class TimeDeltaField(models.PositiveIntegerField):

	descrption = "datetime.timedelta"
	
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
		return value
