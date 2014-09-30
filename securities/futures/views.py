from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, renderers, status
from rest_framework.decorators import action, api_view, renderer_classes
import models, serializers

class FutureAPIViewSet(ModelViewSet):
	
	model = models.Future
	serializer_class = serializers.FutureSerializer
	
class GoodsAPIViewSet(ModelViewSet):

	model = models.Goods
	serializer_class = serializers.GoodsSerializer
