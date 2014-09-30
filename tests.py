#encoding=utf8
from accounts.models import *
from django.contrib.auth.models import User, Group, Permission

user,_ = User.objects.get_or_create(username = 'cpy')
user.set_password('cpy')
user.save()
company = user.profile.create_info(class_name = 'Company', display_name = 'company', industry = '行业')
user,_ = User.objects.get_or_create(username = 'test')
user.set_password('test')
user.save()
user.profile.create_info('Person',assets = 10000,company=Company.objects.get(pk=1), industry = '')
user,_ = User.objects.get_or_create(username = 'test2',)
user.set_password('test')
user.save()
user.profile.create_info('Person', display_name = 'test2', assets = 10000,company=Company.objects.get(pk=1), industry = '')

user,_ = User.objects.get_or_create(username = 'bank')
user.set_password('bank')
user.save()
bank = user.profile.create_info(class_name = 'Bank', assets = 10000)
user,_ = User.objects.get_or_create(username = 'zf')
user.set_password('zf')
user.save()
user.profile.create_info('Government', display_name = u'政府', assets = 10000)
