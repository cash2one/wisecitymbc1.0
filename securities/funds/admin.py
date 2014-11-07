from django.contrib import admin
from models import Fund

class FundAdmin(admin.ModelAdmin):
	fields = ('display_name',)
	list_display = ('display_name',)
	readonly_fields = ('display_name',)

admin.site.register(Fund, FundAdmin)
