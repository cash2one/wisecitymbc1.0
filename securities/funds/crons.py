import cron
from models import Fund
from django.db.models import F

class ShareProfitsCron(cron.Cron):
	
	def do(self):
		for fund in Fund.objects.published():
			fund.share_profits()
			
class CheckPublishCron(cron.Cron):
	
	def get_interval_minutes(self):
		return 1
	
	def do(self): 
		for fund in Fund.objects.filter(published_time__lte = self.now, published = False):
			fund.publish()
			
class CheckFinishCron(cron.Cron):

	def get_interval_minutes(self): 
		return 1
		
	def do(self):
		Fund.objects.published().update(lasted_time = F("lasted_time")-self.delta.seconds)
		for fund in Fund.objects.published().filter(lasted_time__lte = 0):
			fund.finish()
