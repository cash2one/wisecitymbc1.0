from django.conf.urls import patterns, include, url

urlpatterns = patterns('securities.funds.views',
	url(r'^$', 'funds_list'),
	url(r'^detail/$', 'detail'),
	url(r'^setps/$', 'setps'),
)
