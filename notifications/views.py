from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin, RetrieveModelMixin, ListModelMixin
import models, serializers
from rest_framework.decorators import action
from rest_framework.response import  Response
class NotificationAPIViewSet(GenericViewSet, DestroyModelMixin, RetrieveModelMixin, ListModelMixin):
	
	model = models.Notification
	serializer_class = serializers.NotificationSerializer
		
	@action(methods = ["GET"])	
	def confirm(self, request, *args, **kwargs):
		n = self.get_object()
		n.confirm()
		return Response({})
	
	def get_queryset(self):
		return self.request.user.notifications.all()
