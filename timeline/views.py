from rest_framework.views import APIView
from rest_framework.response import Response
from common.permissions import IsAdminUser
from core import Timeline
from serializers import TimelineSerializer

class TimelineAPIView(APIView):

	permission_classes = ()
	
	def get(self, request):
		return Response(TimelineSerializer(Timeline().get()).data)
		
	def post(self, request):
		return Response(TimelineSerializer({'year':Timeline().incr(),'quarter':1}).data)