from models import *
from accounts.models import Person, Bank
from datetime import datetime

try:
	fund = Fund.objects.all()[0]
except:
	fund = Fund.objects.create(
			publisher = Bank.objects.get(pk=1),
			min_return_rate = 1.0,
			max_return_rate = 4.0,
			return_rate = 1.0,
			initial_money = 1000,
			lasted_time = 1000,
			published_time = datetime.now(),
			fund_type = Fund.OPEN
	)
			
person = Person.objects.get(pk=1)
person.buy_fund(fund, 1000)
fund.share_profits()
fund.publish(True)
fund.create_user('fund', 'fund')
