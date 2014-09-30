from django.conf.urls import patterns, include, url

urlpatterns = patterns('accounts.views',
	url(r'^login/$', 'login', name = 'accounts.login'),
	url(r'^logout/$', 'logout', name = 'accounts.logout'),
	url(r'^companies/$', 'company_index', name = 'accounts.companies'),
	url(r'^profile/$', 'profile', name = 'accounts.profile'),
	url(r'^setps/$', 'set_password', name='accounts.set_password'),
)
