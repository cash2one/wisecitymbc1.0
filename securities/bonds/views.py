from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework import status, renderers
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import models, serializers
from common.exceptions import *
from decimal import Decimal
from .permissions import *

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def detail(request):
	bond_id = request.REQUEST.get('uid', 0)
	bond = get_object_or_404(models.Bond, pk = bond_id)
	bond_data = serializers.BondSerializer(bond).data
	is_self = bond.publisher.profile.user.id == request.user.id
	account = request.user.profile.info
	if not is_self and request.user.has_perm('bonds.has_bond'):
		try:
			share = account.bond_shares.get(bond = bond)
		except models.Share.DoesNotExist:
			share = None
	else:
		share = None
	return Response({'share': share, 'object': bond, 'uid': bond_id, 'is_self': is_self}, template_name = 'securities/bonds/detail.html')
	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def bonds_list(request):
	return Response(template_name = 'securities/bonds/list.html')

class ShareAPIViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
	
	model = models.Share
	serializer_class = serializers.ShareSerializer
	permission_classes = [HasBond, HasBondShare]
	
	def get_queryset(self):
		bond_pk = self.kwargs.get('bond_pk', None)
		qs = self.request.user.profile.info.bond_shares.all()
		if bond_pk is not None:
			qs = qs.filter(bond_id = bond_pk)
			
		return qs
		
class BondAPIViewSet(ModelViewSet):

	model = models.Bond
	serializer_class = serializers.BondSerializer
	
	@action(methods = ['GET'], permission_classes = [HasBondObject, OwnBond])
	def ransom(self, request, *args, **kwargs):
		self.get_object().ransom()
		return Response('OK', status = status.HTTP_200_OK)
		
	@action(methods = ['POST'], permission_classes = [HasBond])
	def buy(self, request, *args, **kwargs):
		se = serializers.ApplySerializer(data = request.DATA, actor = request.user.profile.info, bond = self.get_object())
		if se.is_valid():
			return Response('OK')
		else:
			return Response(se.errors, status = status.HTTP_400_BAD_REQUEST)
