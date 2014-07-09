from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework import status, renderers
from rest_framework.response import Response
from django.contrib import auth
from django.shortcuts import get_object_or_404
import models, serializers
from common.exceptions import *
from decimal import Decimal
from permissions import *
from captcha.decorators import check_captcha

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def detail(request):
	fund_id = request.REQUEST.get('uid', 0)
	fund = get_object_or_404(models.Fund, pk = fund_id)
	is_self = (fund.published and fund.account and fund.account.profile.user.id == request.user.id) or \
						(not fund.published and fund.publisher.profile.user.id == request.user.id)
	return Response({'object': fund, 'uid': fund_id,'is_self': is_self}, template_name = 'securities/funds/detail.html')
	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def funds_list(request):
	return Response(template_name = 'securities/funds/list.html')

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def setps(request):
	fund_id = request.REQUEST.get('uid', 0)
	fund = get_object_or_404(models.Fund, pk = fund_id)
	return Response({'object': fund, 'uid': fund_id}, template_name = 'securities/funds/setps.html')	
	
class ShareAPIViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
	
	model = models.Share
	serializer_class = serializers.ShareSerializer
	permission_classes = [HasFund]
	
	def get_queryset(self):
		fund_pk = self.kwargs.get('fund_pk', None)
		qs = self.request.user.profile.info.fund_shares.all()
		if fund_pk is not None:
			qs = qs.filter(fund_id = fund_pk)
			
		return qs
		
class FundAPIViewSet(ModelViewSet):

	model = models.Fund
	serializer_class = serializers.FundSerializer
	
	def create(self, request, *args, **kwargs):
		return super(FundAPIViewSet, self).create(request, publisher = request.user.profile.info, *args, **kwargs)
	
	@action(methods = ['POST'])
	def account(self, request, *args, **kwargs):
		se = serializers.CreateAccountSerializer(data = request.DATA, fund = self.get_object())
		if se.is_valid():
			return Response({'id':se.object.id})
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)	
	
	@action(methods = ['POST'], permission_classes = [HasFund])
	@check_captcha()
	def ransom(self, request, *args, **kwargs):
		se = serializers.ApplySerializer(data = request.DATA, fund = self.get_object(), command = 'ransom', actor = request.user.profile.info)
		if se.is_valid():
			return Response('OK')
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)
	
	@action(methods = ['POST'], permission_classes = [HasFund])
	@check_captcha()
	def buy(self, request, *args, **kwargs):
		se = serializers.ApplySerializer(data = request.DATA, fund = self.get_object(), command = 'buy', actor = request.user.profile.info)
		if se.is_valid():
		#	se.save()
			return Response('OK')
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)
