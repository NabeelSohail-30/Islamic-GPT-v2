from django.urls import path
from . import views

app_name = 'add_data'

urlpatterns = [
    path('', views.add_data_view, name='add_data_form'),
]
