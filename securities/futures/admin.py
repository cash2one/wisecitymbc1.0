from django.contrib import admin
from .models import Future, Goods

class FutureAdmin(admin.ModelAdmin):
	pass

class GoodsAdmin(admin.ModelAdmin):
	pass

admin.site.register(Future, FutureAdmin)
admin.site.register(Goods, GoodsAdmin)
