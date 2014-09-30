from django.contrib import admin
from django.contrib.auth.models import User, Group

class UserAdmin(admin.ModelAdmin):
	fields = ('username','is_superuser', 'is_staff')
	list_display = ('username','is_superuser',)
	#readonly_fields = ('username', 'is_superuser')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
