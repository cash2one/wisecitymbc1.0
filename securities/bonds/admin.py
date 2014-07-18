from django.contrib import admin
from models import Bond

class BondAdmin(admin.ModelAdmin):
	fields = ('display_name',)
	list_display = ('display_name',)
	readonly_fields = ('display_name',)

admin.site.register(Bond, BondAdmin)
