from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin, RetrieveModelMixin, ListModelMixin
import models, serializers
from rest_framework.decorators import action
from rest_framework.response import  Response
from django.db.models import Q
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

class NotificationAPIViewSet(GenericViewSet, DestroyModelMixin, RetrieveModelMixin, ListModelMixin):
	
	model = models.Notification
	serializer_class = serializers.NotificationSerializer
	permission_classes = (IsAuthenticated,)
	filter_fields = ('unread',)
	ordering = ['-important','-created_time']
		
	@action(methods = ["GET"])	
	def confirm(self, request, *args, **kwargs):
		n = self.get_object()
		n.unread = False
		n.save()
		n.confirm()
		return Response({})
	
	def list(self, request, *args, **kwargs):
		now = request.REQUEST.get('now','')
		print request.REQUEST
		if now:
			qs = self.get_queryset().filter(unread = True)
			if now == 'a':
				qs = qs.filter(Q(created_time__gt = datetime.now()-timedelta(seconds = 45)))
			print qs
		else:
			qs = self.filter_queryset(self.get_queryset())
		data = self.get_pagination_serializer(self.paginate_queryset(qs)).data
		return Response(data)
	
	def get_queryset(self):
		if not self.request.user.is_authenticated():
			raise Http404
		else:
			return self.request.user.notifications.all()
