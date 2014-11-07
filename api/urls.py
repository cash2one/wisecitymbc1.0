from django.conf.urls import url, patterns, include

from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSetMixin
from rest_framework.views import APIView

from .core import cache

extra_list = []
router = DefaultRouter()
for pattern, obj in cache.get_routers():
	if callable(obj) and not isinstance(obj, type) or isinstance(obj, (str, unicode)):
		extra_list.append(url(pattern, obj))
	elif issubclass(obj, ViewSetMixin):
		router.register(pattern, obj)
	elif issubclass(obj, APIView):
		extra_list.append(url(pattern, obj.as_view()))
				
extra_list.append(url(r'^', include(router.urls)))

urlpatterns = patterns('',
	url(r'^auth/', include('rest_framework.urls', namespace = 'rest_framework')),
	url(r'^root/$', 'api.views.root',),
	*extra_list
)
