from django.contrib import admin
from models import Stock

class StockAdmin(admin.ModelAdmin):
	fields = ('display_name','current_price')
	list_display = ('display_name','current_price')
	readonly_fields = ('display_name',)

admin.site.register(Stock, StockAdmin)
