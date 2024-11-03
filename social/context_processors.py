from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Notification, Friendship, Room


def get_unread_notifications_count(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(is_read=False, recipient=request.user).count()
        return {'unread_notifications': unread_notifications}
    else:
        return {'unread_notifications': 0}


def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user)[:5]
        return {'header_notifications': notifications}
    else:
        return {'header_notifications': []}


def get_friends(request):
    if request.user.is_authenticated:
        user = request.user
        friendships = Friendship.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
        )

        # Lấy danh sách bạn bè từ các yêu cầu kết bạn này
        friends = []
        for friendship in friendships:
            if friendship.sender == user:
                friends.append(friendship.receiver)
            else:
                friends.append(friendship.sender)

        return {'friends': friends}
    else:
        return {'friends': []}


def get_rooms(request):
    if request.user.is_authenticated:
        rooms = Room.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        rooms = [room for room in rooms if room.messages.count() > 0]
        for room in rooms:
            room.latest_message = room.messages.order_by('-timestamp')[0]
            room.target_user = room.user1 if request.user != room.user1 else room.user2
        return {'rooms': rooms}
    else:
        return {'rooms': []}