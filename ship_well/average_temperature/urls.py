from django.urls import path

from .views import average_temperature


urlpatterns = [
    path('', average_temperature, name='average_temperature'),
]
