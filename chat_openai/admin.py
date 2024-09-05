from django.contrib import admin
from .models import OpenAiMessage
from .model_message import Messages

# Register your models here.
admin.site.register(OpenAiMessage)
admin.site.register(Messages)
