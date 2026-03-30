from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('mylife/', include('mylife.urls')),
    path('', admin.site.urls),
]
