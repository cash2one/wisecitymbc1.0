from django.core.cache import cache 
from django.db import models 
from django.conf import settings 

DOMAIN_CACHE_PREFIX = settings.CACHE_MIDDLEWARE_KEY_PREFIX 
CACHE_EXPIRE = settings.CACHE_MIDDLEWARE_SECONDS 

def cache_key(model, id): 
	 return ("%s-%s-%s" % (DOMAIN_CACHE_PREFIX, model._meta.db_table, 
id)).replace(" ", "") 

class GetCacheManager(models.Manager): 
	# to reload the get method. cache -> db -> cache 
	
	def get(self, *args, **kwargs): 
		id = repr(kwargs) 

		pointer_key = cache_key(self.model, id) 

		model_key = cache.get(pointer_key) 

		if model_key != None: 
			model = cache.get(model_key) 
		if model != None: 
			return model 

		model = super(GetCacheManager, self).get(*args, **kwargs) 

		if not model_key: 
			model_key = cache_key(model, model.pk) 
			cache.set(pointer_key, model_key, CACHE_EXPIRE) 

		cache.set(model_key, model, CACHE_EXPIRE) 

		return model 

class ModelWithGetCache(models.Model): 
	# to reload the save method 
	def save(self, *args, **kwargs): 
		# first, delete cache {model_key -> model} 
		model_key = cache_key(self, self.pk) 
		cache.delete(model_key) 

		super(ModelWithGetCache, self).save() 

	# to reload the delete method 
	def delete(self, *args, **kwargs): 
		# first, delete cache {model_key -> model} 
		model_key = cache_key(self, self.pk) 
		cache.delete(model_key) 

		super(ModelWithGetCache, self).delete() 
