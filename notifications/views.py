from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin, RetrieveModelMixin, ListModelMixin
import models, serializers
from rest_framework.decorators import action
from rest_framework.response import  Response
from django.db.models import Q
from datetime import datetime, timedelta

class NotificationAPIViewSet(GenericViewSet, DestroyModelMixin, RetrieveModelMixin, ListModelMixin):
	
	model = models.Notification
	serializer_class = serializers.NotificationSerializer
		
	@action(methods = ["GET"])	
	def confirm(self, request, *args, **kwargs):
		n = self.get_object()
		n.confirm()
		n.unread = False
		n.save()
		return Response({})
	
	@action(methods = ["GET"])
	def read(self, request, *args, **kwargs):
		n = self.get_object()
		n.unread = False
		n.save()
		return Response({})
	
	def list(self, request, *args, **kwargs):
		now = request.REQUEST.get('now','')
		qs = self.get_queryset().filter(unread = True)
		if now:
			qs = qs.filter(created_time__gt = datetime.now()-timedelta(seconds = 30))
		data = self.get_pagination_serializer(self.paginate_queryset(qs)).data
		#qs.exclude(important = True).mark_all_as_read()
		return Response(data)
	
	def get_queryset(self):
		return self.request.user.notifications.all()
