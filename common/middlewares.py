from django.db import connection
from django.http import HttpResponseRedirect

class SQLMiddleware(object):

	def process_response(self, request, response):
		print "SQL: %d;URL: %s" % (len(connection.queries), request.META['PATH_INFO'])
		return response
