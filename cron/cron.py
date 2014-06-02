from datetime import datetime

class Cron(object):
	
	interval_minutes = 5
	accuracy = 5
	
	def __init__(self):
		self.now = datetime.now()
	
	def get_interval_minutes(self):
		return 5
	
	def check_time(self, time, now):
		print time, now
		return (now-time).seconds>=self.interval_minutes*60-self.accuracy
	
	def do(self):
		pass
	
	def execute(self, time):
		if time is not None and not self.check_time(time, self.now):
			return False
			
		self.do()
		
		return True