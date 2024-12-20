from django.urls import path , include
from .consumers import ChatConsumer, NotificationConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', ChatConsumer.as_asgi()),
    path('notifications/' , NotificationConsumer.as_asgi()),
]
