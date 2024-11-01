from .models import Notification

def get_unread_notifications_count(request):
    unread_notifications = Notification.objects.filter(is_read=False, recipient=request.user).count()
    return {'unread_notifications': unread_notifications}


def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)[:5]
    return {'header_notifications': notifications}


