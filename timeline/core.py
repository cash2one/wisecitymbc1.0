from sae import kvdb
from datetime import datetime
import signals

from rest_framework.exceptions import APIException

class TimelineNotExpiredError(APIException):
	
	status_code = 400
	default_detail = 'The timeline hasn\'t been expired.'

def check(func):
	
	def	wrapper(self, *args, **kwargs):
		data = self.client.get_multi(['set_time','year'])
		self.set_time, self.year = data.pop('set_time',None), data.pop('year',None)
		if self.set_time and (datetime.now()-self.set_time).seconds < self.MIN_TIMELINE:
			raise TimelineNotExpiredError
		year = func(self, *args, **kwargs)
		send = kwargs.pop('send',True)
		if send:
			signals.timeline_changed.send(sender = year, year = year)		
			
		return year
	
	return wrapper
	
class Timeline(object):

	MIN_TIMELINE = 10800
	
	def __init__(self):
		self.__KVClient = None
	
	@property
	def client(self):
			return self.__KVClient or kvdb.KVClient(debug = 1)

	@check
	def incr(self, create_on_none = True):
		self.client.set('set_time', datetime.now())
		if self.year:
			self.client.set('year', self.year+1)
			year = self.year+1
		else:
			year=datetime.now().year
			self.client.set('year',year)
		
		return year
		
	def get_quarter(self,delta):
		quarter=delta.seconds//(self.MIN_TIMELINE//4)+1
		if quarter>4:
			quarter=4
		return quarter
		
	def get(self, create_on_none = True):
		year = self.client.get('year')
		if not year:
			if not create_on_none:
				return None
			else:
				year = datetime.now().year
				self.set(year, send = False)
			
		delta=datetime.now()-self.client.get('set_time')
		return {
				'year': year,
				'time_delta': delta,
				'quarter':self.get_quarter(delta)
		}
	
	@check
	def set(self, year, send = True):
		self.client.set('year', year)
		self.client.set('set_time', datetime.now())
		return year