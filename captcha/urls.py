from django.conf.urls import patterns, url, include

urlpatterns = patterns('captcha.views',
	url('^$', 'index'),
)
