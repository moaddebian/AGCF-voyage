from django.contrib import admin
from .models import (
    Gare,
    Train,
    ArretIntermediaire,
    CarteReduction,
    CarteReductionUtilisateur,
    Reservation,
    Passager,
    OffrePromotion,
    RetardTrain,
    MaintenanceTrain,
)


@admin.register(Gare)
class GareAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'code']
    search_fields = ['nom', 'ville', 'code']


class ArretIntermediaireInline(admin.TabularInline):
    """Inline pour ajouter des arrêts intermédiaires directement dans le formulaire du train"""
    model = ArretIntermediaire
    extra = 3  # Afficher 3 lignes vides par défaut pour faciliter l'ajout
    fields = ('gare', 'ordre', 'heure_passage')
    ordering = ('ordre',)
    verbose_name = "Arrêt intermédiaire"
    verbose_name_plural = "Arrêts intermédiaires"
    autocomplete_fields = ['gare']  # Améliore la recherche de gares
    can_delete = True  # Permet de supprimer des arrêts


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ['numero', 'gare_depart', 'gare_arrivee', 'heure_depart', 'heure_arrivee', 'prix_base', 'places_disponibles', 'nombre_voitures', 'actif']
    list_filter = ['actif', 'classe', 'gare_depart', 'gare_arrivee']
    search_fields = ['numero', 'gare_depart__nom', 'gare_arrivee__nom']
    inlines = [ArretIntermediaireInline]
    
    class Media:
        js = ('admin/js/train_duree_auto.js',)


@admin.register(ArretIntermediaire)
class ArretIntermediaireAdmin(admin.ModelAdmin):
    list_display = ['train', 'gare', 'ordre', 'heure_passage']
    list_filter = ['train', 'gare']
    search_fields = ['train__numero', 'gare__nom', 'gare__ville']
    ordering = ['train', 'ordre']
    list_editable = ['ordre', 'heure_passage']  # Permet d'éditer directement depuis la liste
    autocomplete_fields = ['gare']  # Améliore la recherche de gares


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


@admin.register(RetardTrain)
class RetardTrainAdmin(admin.ModelAdmin):
    list_display = ['train', 'date_voyage', 'minutes_retard', 'statut']
    list_filter = ['statut', 'date_voyage', 'train']
    search_fields = ['train__numero', 'train__gare_depart__ville', 'train__gare_arrivee__ville']


@admin.register(MaintenanceTrain)
class MaintenanceTrainAdmin(admin.ModelAdmin):
    list_display = ['train', 'type_maintenance', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut', 'date_debut', 'date_fin']
    search_fields = ['train__numero', 'type_maintenance', 'responsable']
