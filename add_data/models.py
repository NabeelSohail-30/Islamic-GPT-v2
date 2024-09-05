from django.db import models


class New_Data(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.data[:50]  # Display a portion of the data in admin
