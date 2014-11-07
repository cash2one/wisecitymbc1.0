from .core import Captcha
from .exceptions import CaptchaVerifyFailed
from inspect import getargspec

def check_captcha(field_name = 'captcha'):

	def outer(func):
		
		def func_inner(request, *args, **kwargs):
			captcha = Captcha(request)
			if not captcha.check(request.DATA.get(field_name, None)):
				raise CaptchaVerifyFailed
				
			return func(request, *args, **kwargs)
			
		def method_inner(self, request, *args, **kwargs):
			captcha = Captcha(request)
			if not captcha.check(request.DATA.get(field_name, None)):
				raise CaptchaVerifyFailed
				
			return func(self, request, *args, **kwargs)
					
		if 'self' in getargspec(func).args:
			return method_inner
		else:
			return func_inner
		
	return outer