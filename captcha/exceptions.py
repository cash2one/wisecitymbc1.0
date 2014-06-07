from rest_framework.exceptions import APIException

class CaptchaVerifyFailed(APIException):

	status_code = 400
	default_details = "Captcha not correct."
