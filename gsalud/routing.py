from django.urls import re_path
from gsalud.consumers.user_records_consumer import TableUpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/table_update/(?P<token>[\w\.-]+)/$', TableUpdateConsumer.as_asgi()),
]