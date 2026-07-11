from django.urls import path
from . import views

app_name = 'mylife'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/get_exchange_rate/', views.get_exchange_rate, name='get_exchange_rate'),
]
