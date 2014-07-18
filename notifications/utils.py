from models import Notification

def send_notification(recipient, actor, verb, target):
	return Notification.objects.create(recipient = recipient, actor = actor, verb = verb, target = target)
	
def send_notifications(arg_lists):
	return Notification.bulk_create((Notification(**arg) for arg in arg_lists))
