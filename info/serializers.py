#encoding=utf-8
from rest_framework import serializers
from sae import kvdb

client = kvdb.KVClient()

def validate_percent(value):
	if not 0 < value < 100:
		raise serializers.ValidationError(u"百分比不得超过100或低于0。")

class InfoSerializer(serializers.Serializer):
	
	inflation_rate = serializers.DecimalField(validators = [validate_percent])
	profit_rate = serializers.DecimalField(validators = [validate_percent])
	
	@classmethod
	def get_object(cls):
		res = {}
		for key in cls.base_fields.keys():
			res[key] = client.get(key) or ''
			
		return res
	
	def restore_object(self, attrs, instance = None):
		for key, value in attrs.iteritems():
			client.set(key, value)
		return self.get_object()
