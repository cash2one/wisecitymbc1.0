from common.mixins import *

__all__ = ['CanWriteMixin']

class CanWriteMixin(models.Model):

	permission = 'publish_passage'	
	
	class Meta:
		abstract = True
