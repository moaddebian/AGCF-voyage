from django.contrib import admin
from .models import Gare, Train, CarteReduction, CarteReductionUtilisateur, Reservation, Passager, OffrePromotion


@admin.register(Gare)
class GareAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'code']
    search_fields = ['nom', 'ville', 'code']


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ['numero', 'gare_depart', 'gare_arrivee', 'heure_depart', 'heure_arrivee', 'prix_base', 'places_disponibles', 'actif']
    list_filter = ['actif', 'classe', 'gare_depart', 'gare_arrivee']
    search_fields = ['numero', 'gare_depart__nom', 'gare_arrivee__nom']


@admin.register(CarteReduction)
class CarteReductionAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_carte', 'reduction_pourcentage', 'actif']
    list_filter = ['type_carte', 'actif']


@admin.register(CarteReductionUtilisateur)
class CarteReductionUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'carte', 'numero_carte', 'date_expiration']
    list_filter = ['carte', 'date_expiration']
    search_fields = ['utilisateur__username', 'numero_carte']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['code_reservation', 'utilisateur', 'train', 'date_voyage', 'prix_total', 'statut', 'date_reservation']
    list_filter = ['statut', 'mode_paiement', 'date_voyage']
    search_fields = ['code_reservation', 'utilisateur__username']
    readonly_fields = ['code_reservation', 'date_reservation']


@admin.register(Passager)
class PassagerAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'date_naissance', 'reservation']
    search_fields = ['nom', 'prenom']


@admin.register(OffrePromotion)
class OffrePromotionAdmin(admin.ModelAdmin):
    list_display = ['titre', 'reduction_pourcentage', 'date_debut', 'date_fin', 'actif']
    list_filter = ['actif', 'date_debut', 'date_fin']

