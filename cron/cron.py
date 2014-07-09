from datetime import datetime, timedelta

class Cron(object):
	
	accuracy = 5
	
	def __init__(self):
		self.now = datetime.now()
		self.delta = timedelta(seconds = 0)
	
	def get_interval_minutes(self):
		return 5
	
	def check_time(self, delta):
		return delta.seconds>=self.get_interval_minutes()*60-self.accuracy
	
	def do(self):
		pass
	
	def execute(self, time):
		if time is not None:
			self.delta = self.now-time
		if time is not None and not self.check_time(self.delta):
			return False
			
		self.do()
		
		return True
