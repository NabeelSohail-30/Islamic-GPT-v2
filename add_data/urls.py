from django.urls import path
from . import views

app_name = 'add_data'

urlpatterns = [
    path('view', views.add_data_view, name='view'),
]
