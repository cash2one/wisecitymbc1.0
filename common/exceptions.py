from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler
from django.http import HttpResponseRedirect

class AssetsNotEnough(APIException):
	
	status_code = status.HTTP_400_BAD_REQUEST
	default_detail = 'The assets in your account is not enough.'
	
class ParamError(APIException):
	
	status_code = status.HTTP_400_BAD_REQUEST
	
def handle_403_exception(exception):
	response = exception_handler(exception)
	if response and response.status_code == 403:
		return HttpResponseRedirect('/accounts/login/')
	return response
