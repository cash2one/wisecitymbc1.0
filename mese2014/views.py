from annoying.decorators import render_to
from django.http import HttpResponse
from securities.futures import models

@render_to("index.html")
def index(request):
	return {
		'futures': models.Future.objects.all(),
		'goods': models.Goods.objects.all()
	}
