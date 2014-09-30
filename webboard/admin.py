#encoding=utf8
from django.contrib import admin
from .models import Passage

class PassageAdmin(admin.ModelAdmin):
	exclude = ('attachments',)
	readonly_fields = ('author',)
	
admin.site.register(Passage, PassageAdmin)
