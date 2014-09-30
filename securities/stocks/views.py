from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, renderers, status
from rest_framework.decorators import action, api_view, renderer_classes, permission_classes
import models, serializers
from accounts.models import filter_accounts, account_classes_map
from .exceptions import ParamError
from decimal import Decimal
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import HasStock
from captcha.decorators import check_captcha
from django.http import Http404
from django.contrib.auth.models import User

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def stocks_list(request):
	return Response(template_name = 'securities/stocks/list.html')
	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
@permission_classes([HasStock])
def change_application(request):
	application_id = request.REQUEST.get('uid', '0')
	application_object = get_object_or_404(models.Application, pk = application_id)
	serializer = serializers.StockSerializer(application_object.stock)
	try:
		share = request.user.profile.info.stock_shares.get(stock = stock_object)
	except:
		share = None
	return Response({'share': share, 'object': serializer.data, 'uid': application_id, 'application':application_object}, template_name = 'securities/stocks/change_app.html')
	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
@permission_classes([HasStock])
def detail(request):
	stock_id = request.REQUEST.get('uid', '0')
	stock_object = get_object_or_404(models.Stock, pk = stock_id)
	serializer = serializers.StockSerializer(stock_object)
	application_objects = models.Application.objects.filter(stock = stock_object, shares__gt = Decimal(0))
	applications = serializers.ApplicationSerializer(application_objects, exclude = ['stock'], many = True) 
	my_applications = serializers.ApplicationSerializer(
		request.user.profile.info.stock_applications.filter(stock = stock_object),
		exclude = ['stock'],
		many = True
	)
	try:
		share = request.user.profile.info.stock_shares.get(stock = stock_object)
	except:
		share = None
	return Response({'share': share, 'mys': my_applications.data, 'object': serializer.data, 'uid': stock_id, 'applications':applications.data}, template_name = 'securities/stocks/detail.html')

class LogAPIViewSet(GenericViewSet, mixins.ListModelMixin):
	
	model = models.Log
	serializer_class = serializers.LogSerializer
	
	def get_queryset(self):
		pk = self.kwargs.get('stock_pk', None)
		stock = get_object_or_404(models.Stock, pk = pk)
		return stock.logs.all()

class ShareAPIViewSet(GenericViewSet, mixins.ListModelMixin):
	
	model = models.Share
	serializer_class = serializers.ShareSerializer
	permission_classes = [HasStock]
	
	def get_queryset(self):
		stock_pk = self.kwargs.get('stock_pk', None)
		user_id = self.request.REQUEST.get('uid', 0)
		if user_id:
			user = get_object_or_404(User, pk=user_id)
		else:
			user = self.request.user
			
		qs = user.profile.info.stock_shares.all()
		if stock_pk is not None:
			qs = qs.filter(stock_id = stock_pk)
		return qs
		
class ApplicationAPIViewSet(ModelViewSet):
	
	model = models.Application
	serializer_class = serializers.ApplicationSerializer
	
	def get_queryset(self):
		stock_pk = self.kwargs.get('stock_pk', None)
		qs = models.Application.objects.all()
		if stock_pk is not None:
			qs = qs.filter(stock_id = stock_pk)
			
		return qs

class StockAPIViewSet(ModelViewSet):
	
	serializer_class = serializers.StockSerializer
	model = models.Stock
	
	def create(self, request, *args, **kwargs):
		serializer = serializers.CreateStockSerializer(data = request.DATA)
		if serializer.is_valid():
			return Response(serializers.StockSerializer(serializer.object).data)
		else:
			return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
			
	@check_captcha()
	def apply(self, request, type, *args, **kwargs):
		se = serializers.ApplySerializer(type, self.get_object(), request.user.profile.info, data = request.DATA)
		if se.is_valid():
			res = serializers.ApplicationSerializer(se.save()).data
			s = status.HTTP_200_OK
		else:
			res = se.errors
			s = status.HTTP_400_BAD_REQUEST
			
		return Response(res, status = s)
		
	@action(methods = ['GET'])
	def data(self, request, *args, **kwargs):
		stock = self.get_object()
		data = stock.logs.values('created_time', 'price').order_by('-created_time')
		return Response(data)
		
	@action(methods = ['POST'],permission_classes = [HasStock])
	def buy(self, request, *args, **kwargs):
		return self.apply(request, models.Application.BUY, *args, **kwargs)
		
	@action(methods = ['POST'],permission_classes = [HasStock])
	def sell(self, request, *args, **kwargs):
		return self.apply(request, models.Application.SELL, *args, **kwargs)
