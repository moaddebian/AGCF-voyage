from django.contrib import admin
from .models import ProfilUtilisateur


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'telephone', 'ville', 'date_creation']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'telephone', 'ville']

