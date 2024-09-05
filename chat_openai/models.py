from django.db import models
from django.conf import settings


class OpenAiMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    content = models.TextField()
    role = models.CharField(max_length=4, choices=ROLE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
