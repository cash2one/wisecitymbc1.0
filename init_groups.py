from django.contrib.auth.models import Group, Permission

def perms(*args):
	return Permission.objects.filter(codename__in = args)
	
def create(name, perm_list):
	group,_ = Group.objects.get_or_create(name = name)
	group.permissions = list(perms(*perm_list))
	group.save()
	
create('writer', ['publish_passage'])
