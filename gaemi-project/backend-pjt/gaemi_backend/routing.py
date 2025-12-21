from django.urls import re_path
from notifications.consumers import NotificationConsumer, ChartConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/stocks/(?P<stock_code>\w+)/$', ChartConsumer.as_asgi()),
]