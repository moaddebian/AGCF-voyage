"""
URL configuration for agcf_voyage project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language

# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration AGCF Voyages"
admin.site.site_title = "AGCF Voyages Admin"
admin.site.index_title = "Administration AGCF Voyages"

# La vue d'index reste par défaut - l'analyse est accessible via le bouton flottant

# Ajouter les URLs d'analyse admin AVANT admin.site.urls
from reservations.admin_analytics import AnalyticsAdminView, analytics_data_view

urlpatterns = [
    path('admin/analytics/', admin.site.admin_view(AnalyticsAdminView.analytics_view), name='admin_analytics'),
    path('admin/analytics/data/', admin.site.admin_view(analytics_data_view), name='admin_analytics_data'),
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', include('reservations.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

