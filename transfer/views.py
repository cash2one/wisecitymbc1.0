from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import models, serializers
from common.permissions import IsSubClass
from accounts.models import Bank
from accounts.serializers import BankSerializer
from django.shortcuts import get_object_or_404
from functools import partial
from django.contrib import auth
from django.http import Http404
from decimal import Decimal
from captcha.decorators import check_captcha

@api_view(['POST'])
@permission_classes([IsSubClass('CanTransferMixin')])
#@check_captcha()
def transfer(request, *args, **kwargs):
	data = serializers.TransferSerializer(data = request.DATA, actor = request.user.profile.info)
	if data.is_valid():
		return Response(data.object)
	else:
		return Response(data.errors, status = status.HTTP_400_BAD_REQUEST)

class BankAPIViewSet(ReadOnlyModelViewSet):

	model = Bank
	serializer_class = BankSerializer
	
	@action(methods = ['POST'], permission_classes = [IsSubClass('CanStoreMixin')])
	@check_captcha()
	def store(self, request, *args, **kwargs):
		se = serializers.StoreSerializer(data = request.DATA, actor = request.user.profile.info, bank = self.get_object(), command = 'store')
		if se.is_valid():
			return Response(se.object)
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)
		
	@action(methods = ['POST'], permission_classes = [IsSubClass('CanStoreMixin')])
	@check_captcha()
	def remove(self, request, *args, **kwargs):
		se = serializers.StoreSerializer(data = request.DATA, actor = request.user.profile.info, bank = self.get_object(), command = 'remove')
		if se.is_valid():
			return Response(se.object)
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)

class TransferLogAPIViewSet(ReadOnlyModelViewSet):

	model = models.TransferLog
	serializer_class = serializers.TransferLogSerializer
	permission_classes = (IsSubClass('CanTransferMixin'), IsAuthenticated)
	
	def get_queryset(self):
		log_type = self.kwargs.get('log_type')
		user_id = self.request.REQUEST.get('uid', 0)
		if user_id:
			user = get_object_or_404(auth.models.User, pk=user_id)
		else:
			user = self.request.user
		account = user.profile.info
		if log_type == 'transfer':
			return account.transfer_logs.all()
		else:
			return account.receive_logs.all()

class DepositAPIViewSet(ReadOnlyModelViewSet):

	model = models.Deposit
	serializer_class = serializers.DepositSerializer
	permission_classes = (IsSubClass('CanStoreMixin'),)
	
	def get_serializer_class(self):
		pk = self.kwargs.get('bank_pk', None)
		cls = serializers.DepositSerializer
		if pk is not None:
			cls = partial(cls, exclude = ['bank'])
			
		return cls
	
	def get_queryset(self):
		qs = self.request.user.profile.info.deposits.filter(money__gt = 0)
		pk = self.kwargs.get('bank_pk', None)
		if pk is not None:
			qs = qs.filter(bank_id = pk)
			
		return qs
