from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^cron/', include('cron.urls')),
	url(r'^captcha/', include('captcha.urls')),
	url(r'^$', 'mese2014.views.index', name='index'),
	url(r'^securities/', include('securities.urls')),
	url(r'^stocks/', include('securities.stocks.urls')),
	url(r'^funds/', include('securities.funds.urls')),
	url(r'^bonds/', include('securities.bonds.urls')),
	url(r'^accounts/', include('accounts.urls')),
	url(r'^webboard/', include('webboard.urls')),
	url(r'^file/', include('files.urls')),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^api/', include('api.urls')),
	url(r'^admin/', include(admin.site.urls)),
)
