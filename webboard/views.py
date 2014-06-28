from rest_framework import viewsets, renderers, response, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
import models, serializers
import json
from django.shortcuts import render_to_response
from annoying.decorators import render_to

from .permissions import CanWrite

def test(a):
	return render_to_response('p_test.html')

@render_to('wb/write.html')
def write(request):
	return {}
	
class BasePassageViewSet(viewsets.GenericViewSet):

	model = models.Passage
	serializer_class = serializers.PassageSerializer
	
	def get_queryset(self):
		_type = self.request.GET.get('type', '').upper()
		queryset = models.Passage.objects.all()
		if _type:
			queryset = queryset.filter(type = _type)
		return queryset	

class PassageRetrieveViewSet(BasePassageViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

	renderer_classes = (renderers.TemplateHTMLRenderer,renderers.JSONRenderer)
	
	def list(self, *args, **kwargs):
		response = super(PassageRetrieveViewSet, self).list(*args, **kwargs)
		response.template_name = 'wb/passages.html'
		return response
		
	def retrieve(self, *args, **kwargs):
		super(PassageRetrieveViewSet, self).retrieve(*args, **kwargs)
		response = Response({'object':serializers.PassageSerializer(self.object).data})
		response.template_name = 'wb/detail.html'
		return response
		
	@action(methods = ['GET'])
	def change(self, *args, **kwargs):
		response = Response({'object':serializers.PassageSerializer(self.get_object()).data})
		response.template_name = 'wb/change.html'
		return response		
	
class PassageAPIViewSet(BasePassageViewSet, viewsets.ModelViewSet):
	
	permission_classes = (CanWrite,)
	filter_fields = ('type', "author")

	def get_queryset(self):
		queryset = models.Passage.objects.all()
		if self.request.QUERY_PARAMS.get('type','') == 'all':
			queryset = queryset.exclude(type = 'ENT')
		return queryset

	def create(self, request, *args, **kwargs):
		super(PassageAPIViewSet, self).create(request, author = request.user.id, *args, **kwargs)	
		return response.Response({'url': '/webboard/passages/%d/' % self.object.id})
		
	def update(self, request, *args, **kwargs):
		super(PassageAPIViewSet, self).update(request, author = request.user.id, *args, **kwargs)	
		return response.Response({'url': '/webboard/passages/%d/' % self.object.id})
		
	def list(self, request, *args, **kwargs):
		#self.serializer_options = {'exclude':['content']}
		return super(PassageAPIViewSet,self).list(self,request,*args,**kwargs)
	
class CommentAPIViewSet(viewsets.ModelViewSet):

	model = models.Comment
	serializer_class = serializers.CommentSerializer
	
	def get_queryset(self):
		passage_pk = int(self.kwargs['passage_pk'])
		return get_object_or_404(models.Passage, pk = passage_pk).comments.all()
		
	def create(self, request, *args, **kwargs):
		res = super(CommentAPIViewSet, self).create(request, passage = kwargs['passage_pk'], author = request.user.id, *args, **kwargs)
		self.object.send()
		return res
