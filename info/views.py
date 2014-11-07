# Create your views here.
from rest_framework.views import APIView
import serializers
from rest_framework.response import Response
from rest_framework import status

class InfoAPIViewSet(APIView):

	serializer_class = serializers.InfoSerializer
	
	def get(self, request, *args, **kwargs):
		data = self.serializer_class.get_object()
		return Response(data = data)
		
	def patch(self, request, *args, **kwargs):
		serializer = self.serializer_class(data = request.DATA, partial = True)
		if serializer.is_valid():
			return Response(data = serializer.object)
		else:
			return Response(data = serializer.errors, status = status.HTTP_400_BAD_REQUEST)
