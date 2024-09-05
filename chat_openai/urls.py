from django.urls import path
from .views import view_chat, chat, export_messages_csv

app_name = 'chat_openai'

urlpatterns = [
    path('view', view_chat, name='view'),
    path('chat', chat, name='chat'),
    path('export_messages_csv', export_messages_csv, name='export_messages_csv'),
]
