from django.shortcuts import render_to_response
from django.template import RequestContext
def root(request):
	return render_to_response('root.html', {}, context_instance = RequestContext(request))
