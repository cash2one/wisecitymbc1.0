#encoding=utf8
from .models import Notification
from string import Template

def send_notifications(data):
	return Notification.objects.create_notifications(data)

def send_notification(**kwargs):
	return Notification.objects.create_notification(**kwargs)
	
class Dispatcher(object):
	
	def __init__(self, fmt):
		self.fmt = None
		if isinstance(fmt, (unicode, str)):
			self.fmt = fmt
			self.temps = {'_': Template(fmt)}
		else:
			self.fmts = fmt
			self.temps = {}
			for key, f in self.fmts.iteritems():
				self.temps[key] = Template(f)
			
	def get_fmt(self, key):
		if self.fmt is not None:
			return self.fmt
			
		return self.fmts.get(key, '')
		
	def format(self, key, data):
		if self.fmt is not None:
			key = '_'
		_data = {key: unicode(value) for key, value in data.iteritems()}
		return self.temps[key].safe_substitute(_data)
		
	def send(self, key, args, **kwargs):
		msg = self.format(key, args)
		return send_notification(message = msg, **kwargs)
		
	def multi_send(self, key, data):
		for i in data:
			msg = self.format(key, i.pop('args',{}))
			i['message'] = msg
			
		return send_notifications(data)	
