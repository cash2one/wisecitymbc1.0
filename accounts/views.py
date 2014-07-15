#encoding=utf-8
from django.contrib import auth
from django.shortcuts import render_to_response, get_object_or_404
from annoying.decorators import ajax_by_method
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, generics, mixins, viewsets, permissions, status, renderers
from rest_framework.decorators import *
from rest_framework.response import Response

from common.exceptions import ParamError
from captcha.decorators import check_captcha
from securities.funds.serializers import FundSerializer

import models, serializers
import json

from django.contrib.auth.decorators import login_required

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def set_password(request):
	return Response(template_name = 'accounts/set_password.html')

@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def company_index(request):
	res = serializers.get_enterprises()
	return Response({'companies':res}, template_name = 'accounts/companies.html')
	
@api_view(['GET'])
@renderer_classes([renderers.JSONRenderer])
def companies(request):
	data = models.filter_accounts(account_type=['company', 'fundcompany', 'bank'])
	_ = []
	for i in data:
		i.pop('class')
		_.append(i)
	return Response(_)
	
@login_required	
@api_view(['GET'])
@renderer_classes([renderers.TemplateHTMLRenderer])
def profile(request):

	class Perm(object):
		def __init__(self, user):
			self.__permissions = user.user_permissions.values_list('codename')
			
		def __getattr__(self, name):
			return (name,) in self.__permissions

	uid = request.REQUEST.get('uid', None)
	if uid is not None:
		user_obj = get_object_or_404(auth.models.User, id = uid)
		is_self = user_obj == request.user
	else:
		uid = request.user.id
		user_obj = request.user
		is_self = True
		
	fund = None
	if user_obj.profile.info.account_type == 'fund':
		fund = FundSerializer(user_obj.profile.info.fund).data
		
	data = serializers.UserSerializer(user_obj, safe_fields = False).data
	return Response({
			'fund': fund,
			'user_object': data, 
			'permissions': Perm(user_obj),
			'json': renderers.JSONRenderer().render(data),
			'is_self':is_self}, template_name = 'accounts/profile.html')

class UserAPIViewSet(viewsets.ModelViewSet):
	
	serializer_class = serializers.UserSerializer
	model = auth.models.User
	
	def get_object(self):
		pk = self.kwargs.get('pk', None)
		if pk == 'my':
			return self.request.user
		else:
			return super(UserAPIViewSet, self).get_object()
			
	def list(self, request, *args, **kwargs):
		self.object_list = self.filter_queryset(self.get_queryset())

		if not self.allow_empty and not self.object_list:
			class_name = self.__class__.__name__
			error_msg = self.empty_error % {'class_name': class_name}
			raise Http404(error_msg)

		fields = request.REQUEST.get('fields','')
		if fields:
			fields = fields.split(',')
		page = self.paginate_queryset(self.object_list)
		if page is not None:
			serializer = self.get_pagination_serializer(page, profile_fields = fields)
		else:
			serializer = self.get_serializer(self.object_list, many=True, profile_fields = fields)

		return Response(serializer.data)
			
	def retrieve(self, request, *args, **kwargs):
		self.object = self.get_object()
		fields = request.REQUEST.get('fields', [])
		if fields:
			fields = fields.split(',')
		serializer = self.get_serializer_class()(self.object, profile_fields = fields)
		return Response(serializer.data)
			
	def create(self, request, *args, **kwargs):
		serializer = serializers.CreateUserSerializer(data = request.DATA)
		if serializer.is_valid():
			return Response(serializers.UserSerializer(serializer.object).data)
		else:
			return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
	
	@action(methods=['POST'])
	@check_captcha()
	def set_password(self, request, *args, **kwargs):
		old_password = request.DATA.get('old_password','')
		new_password = request.DATA.get('new_password','')
		if not request.user.check_password(old_password):
			raise ParamError
		request.user.set_password(new_password)
		request.user.save()
		return Response("OK")
	
	@action(methods=['POST'])
	def dec(self, request, *args, **kwargs):
		data = dict(request.DATA)
		data['account'] = self.get_object().profile.info
		serializer = serializers.DecAssetsSerializer(data = data)
		if serializer.is_valid():
			return Response('OK')
		else:
			return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
	
	@action(methods=['GET', 'PATCH'])
	def profile(self, *args, **kwargs):
		profile = self.get_object().profile.info
		
		if self.request.method == 'GET':
			serializer_class = serializers.get_serializer_by_object(profile)
			return Response(serializer_class(profile).data)
		elif self.request.method == 'PATCH':
			serializer = serializers.get_serializer_by_object(profile)(profile, data = self.request.DATA, partial = True)
			if not serializer.is_valid():
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			profile = serializer.save(force_update=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
	
@csrf_exempt
def login(request):
	if request.method == 'GET':
		http_referer = request.META.get('HTTP_REFERER', '/')
		request.session['referer'] = http_referer
		return render_to_response('accounts/login.html')
	#POST
	username = request.POST.get('username', '')
	password = request.POST.get('password', '')
	user = auth.authenticate(username = username, password = password)
	if user is None:
		return HttpResponse('',status=status.HTTP_400_BAD_REQUEST)
	else:
		auth.login(request, user)
		return HttpResponse(json.dumps({'status':'success', 'referer': request.session['referer']}))
		
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')
