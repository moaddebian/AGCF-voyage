from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.home, name='home'),
    path('gerer-reservation/', views.gerer_reservation_public, name='gerer_reservation'),
    path('retards/', views.gestion_retards, name='gestion_retards'),
    path('maintenance/', views.gestion_maintenance, name='gestion_maintenance'),
    path('recherche/<int:gare_depart_id>/<int:gare_arrivee_id>/<str:date_depart>/<str:heure_depart>/<int:gare_intermediaire_id>/', views.recherche_resultats, name='recherche_resultats_heure'),
    path('recherche/<int:gare_depart_id>/<int:gare_arrivee_id>/<str:date_depart>/<int:gare_intermediaire_id>/', views.recherche_resultats, name='recherche_resultats'),
    # URLs de compatibilité pour les anciennes recherches sans gare intermédiaire
    path('recherche/<int:gare_depart_id>/<int:gare_arrivee_id>/<str:date_depart>/<str:heure_depart>/', views.recherche_resultats, name='recherche_resultats_heure_old'),
    path('recherche/<int:gare_depart_id>/<int:gare_arrivee_id>/<str:date_depart>/', views.recherche_resultats, name='recherche_resultats_old'),
    path('reserver/<int:train_id>/', views.reserver_train, name='reserver_train'),
    path('ajouter-passagers/', views.ajouter_passagers, name='ajouter_passagers'),
    path('paiement/', views.paiement, name='paiement'),
    path('confirmation/<str:code>/', views.confirmation, name='confirmation'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('reservation/<str:code>/', views.detail_reservation, name='detail_reservation'),
    path('reservation/<str:code>/annuler/', views.annuler_reservation, name='annuler_reservation'),
    path('reservation/<str:code>/telecharger/', views.telecharger_billet, name='telecharger_billet'),
    path('telecharger-billet/<str:code>/', views.telecharger_billet_public, name='telecharger_billet_public'),
    path('offres/', views.offres_promotions, name='offres_promotions'),
    path('panier/', views.panier, name='panier'),
    path('change-language/', views.change_language_ajax, name='change_language_ajax'),
]

