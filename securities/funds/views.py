from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework import status, renderers
from rest_framework.response import Response
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import models, serializers
from common.exceptions import *
from decimal import Decimal
from permissions import *

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def detail(request):
	fund_id = request.REQUEST.get('uid', 0)
	fund = get_object_or_404(models.Fund, pk = fund_id)
	return Response({'object': fund, 'uid': fund_id}, template_name = 'securities/funds/detail.html')
	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def funds_list(request):
	return Response(template_name = 'securities/funds/list.html')

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
	
	@action(methods = ['POST'], permission_classes = [HasFund])
	def ransom(self, request, *args, **kwargs):
		money = request.DATA.get('money', None)
		if money is None:
			raise ParamError("The field money must be set.")
		account = request.user.profile.info
		account.ransom_fund_share(self.get_object(), money)
		return Response('OK', status = status.HTTP_200_OK)
	
	@action(methods = ['POST'], permission_classes = [HasFund])
	def buy(self, request, *args, **kwargs):
		money = request.DATA.get('money', None)
		if money is None:
			raise ParamError("The field `money` must be set.")
			
		account = request.user.profile.info
		account.buy_fund(self.get_object(), Decimal(money))
		return Response('OK', status = status.HTTP_200_OK)
