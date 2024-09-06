from django.contrib import admin
from .models import New_Data
from .model_file import UploadedFile

# Register your models here.
admin.site.register(New_Data)
admin.site.register(UploadedFile)
