from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import HasReportsMixin, Person
from .utils import check_base_class_by_name

def HasObject(field_name):
	
	class P(BasePermission):
		
		def has_object_permission(self, request, view, obj):
			user = obj
			for attr_name in field_name.split('.'):
				user = getattr(user, attr_name, None)
				if user is None:
					break

			return request.user and request.user == user
	
	return P

def IsSubClass(cls_name, safe_methods = False):
	
	class P(BasePermission):
		
		safe_methods = False
		
		def __init__(self, *args, **kwargs):
			self.safe_methods = self.safe_methods or kwargs.pop('safe_methods', False)
			return super(P, self).__init__(*args, **kwargs)
			
		@classmethod
		def new(cls, safe_methods = False, *args, **kwargs):
			cls.safe_methods = safe_methods
			return cls
		
		def has_permission(self, request, view):
			if self.safe_methods and (request.method in SAFE_METHODS):
				return True
			if not request.user.is_authenticated():
				return False
			if isinstance(cls_name, type):
				condition = isinstance(request.user.profile.info, cls_name)
			else:
				condition = check_base_class_by_name(request.user.profile.info, cls_name)
			return request.user.profile and condition
			
	return P

HasReport = IsSubClass(HasReportsMixin)
		
class IsAdminUser(BasePermission):

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return request.user
		else:
			return request.user and request.user.is_staff
			
class IsPerson(BasePermission):
	
	def has_permission(self, request, view):
		return request.user and isinstance(request.user.profile.info, Person)
		
class OwnsObject(BasePermission):
	
	def has_object_permission(self, request, view, obj):
		return request.user and isinstance(request.user.profile.info, Person) and obj.owner == request.user.profile.info
		
class HasFile(BasePermission):
	
	def has_object_permission(self, request, view, obj):
		user = request.user
		return user and getattr(user.profile.info, user.profile.info.reports_field).bulk_in([obj.pk]).exists()
