from django.conf.urls import patterns, include, url

urlpatterns = patterns('securities.stocks.views',
	url('detail/$', 'detail', name='stocks.detail'),
	url('^$', 'stocks_list', name='stocks.list'),
	url('change/$', 'change_application', name='stocks.change'),
)