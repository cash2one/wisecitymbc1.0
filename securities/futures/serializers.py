from rest_framework import serializers
import models

class FutureSerializer(serializers.ModelSerializer):

	class Meta:
		model = models.Future