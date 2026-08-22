from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('mylife/', include('mylife.urls')),
    path('', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
