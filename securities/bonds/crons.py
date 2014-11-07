import cron
from models import Bond
from django.db.models import F

class ShareProfitsCron(cron.Cron):
	
	def do(self):
		for bond in Bond.objects.published():
			bond.share_profits()
		
class CheckPublishCron(cron.Cron):
	
	def get_interval_minutes(self):
		return 1
	
	def do(self):
		for bond in Bond.objects.filter(published_time__lte = self.now, published = False):
			bond.publish()
			
class CheckFinishCron(cron.Cron):

	def get_interval_minutes(self):
		return 1
		
	def do(self):
		Bond.objects.published().update(lasted_time = F("lasted_time")-self.delta.seconds)
		for bond in Bond.objects.published().filter(lasted_time__lte = 0):
			bond.finish()
