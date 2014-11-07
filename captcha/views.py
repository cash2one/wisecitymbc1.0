from .core import Captcha

def index(request):
	return Captcha(request).display()
