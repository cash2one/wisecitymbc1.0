from django.conf.urls import patterns, include, url

urlpatterns = patterns('securities.bonds.views',
	url(r'^detail/$', 'detail'),
	url(r'^$', 'bonds_list'),
)
