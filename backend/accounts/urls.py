from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(template_name='accounts/connexion.html'), name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),
    path('profil/', views.profil, name='profil'),
    path('ajouter-carte/', views.ajouter_carte_reduction, name='ajouter_carte_reduction'),
    path('supprimer-carte/<int:carte_id>/', views.supprimer_carte_reduction, name='supprimer_carte_reduction'),
    path('supprimer-compte/', views.supprimer_compte, name='supprimer_compte'),
]

