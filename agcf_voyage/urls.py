"""
URL configuration for agcf_voyage project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration AGCF Voyages"
admin.site.site_title = "AGCF Voyages Admin"
admin.site.index_title = "Administration AGCF Voyages"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservations.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

