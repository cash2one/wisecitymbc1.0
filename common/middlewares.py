from django.db import connection
from django.http import HttpResponseRedirect

class SQLMiddleware(object):

	def process_response(self, request, response):
		print "SQL: %d;URL: %s" % (len(connection.queries), request.META['PATH_INFO'])
		return response
		
class ForbiddenMiddleware(object):
	
	def process_response(self, request, response):
		print request, response
		if not request.META['PATH_INFO'].startswith('/api') and response.status_code == 403:
			return HttpResponseRedirect('/accounts/login/')
