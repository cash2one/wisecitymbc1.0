from django.contrib import admin
from .models import Future

class FutureAdmin(admin.ModelAdmin):
	pass

admin.site.register(Future, FutureAdmin)