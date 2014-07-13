from models import File, PublicFile, PrivateFile
from serializers import PublicFileSerializer, PrivateFileSerializer

from annoying.decorators import ajax_request, render_to
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import DefaultStorage
from django.conf import settings
 
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from common.permissions import HasReport, IsAdminUser, HasFile, IsSubClass

from django.http import Http404

@render_to('upload_test.html')
def index(request):
	return {}

class PublicFileAPIViewSet(ModelViewSet):

	model = File
	serializer_class = PublicFileSerializer
	
	def create(self, request, *args, **kwargs):
		return super(PublicFileAPIViewSet, self).create(request, file_type = File.PUBLIC, *args, **kwargs)	
	
class PrivateFileAPIViewSet(ModelViewSet):
	
	model = PrivateFile
	serializer_class = PrivateFileSerializer
	permission_classes = (HasReport.new(True),)
	
	def dispatch(self, request, *args, **kwargs):
		self.account = request.user.profile.info
		if not hasattr(self.account, 'report_field'):
			raise Http404
		self.field_name = (kwargs['field_name'] or self.account.report_field).replace('-','_')
		print self.field_name
		field = self.account.has_field(self.field_name)
		if self.field_name:
			if not field:
				raise Http404
		return super(PrivateFileAPIViewSet, self).dispatch(request, *args, **kwargs)
	
	def get_queryset(self):
		return getattr(self.account, self.field_name).all()
	
	def get_object(self, *args, **kwargs):
		return super(PrivateFileAPIViewSet, self).get_object(*args, **kwargs)
	
	def create(self, request, *args, **kwargs):
		response = super(PrivateFileAPIViewSet, self).create(request, file_type = File.PRIVATE, *args, **kwargs)
		self.request.user.profile.info.upload_reports(self.object,field_name = self.field_name)
		return response
