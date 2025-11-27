from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import InscriptionForm, ModifierProfilForm, CarteReductionForm
from .models import ProfilUtilisateur
from reservations.models import CarteReductionUtilisateur


def inscription(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('reservations:dashboard')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé avec succès.")
            return redirect('reservations:dashboard')
    else:
        form = InscriptionForm()
    
    return render(request, 'accounts/inscription.html', {'form': form})


@login_required
def profil(request):
    """Vue du profil utilisateur"""
    profil_user, created = ProfilUtilisateur.objects.get_or_create(utilisateur=request.user)
    cartes_reduction = CarteReductionUtilisateur.objects.filter(utilisateur=request.user)
    
    if request.method == 'POST':
        form = ModifierProfilForm(request.POST, instance=profil_user, user=request.user)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('accounts:profil')
    else:
        form = ModifierProfilForm(instance=profil_user, user=request.user)
    
    context = {
        'form': form,
        'cartes_reduction': cartes_reduction,
    }
    return render(request, 'accounts/profil.html', context)


@login_required
def ajouter_carte_reduction(request):
    """Ajouter une carte de réduction"""
    if request.method == 'POST':
        form = CarteReductionForm(request.POST)
        if form.is_valid():
            try:
                carte = form.save(commit=False)
                carte.utilisateur = request.user
                carte.save()
                # Message de succès avec toutes les informations
                messages.success(
                    request, 
                    f"Carte de réduction '{carte.carte.nom}' ajoutée avec succès ! "
                    f"Elle sera automatiquement appliquée lors de vos prochaines réservations (réduction de {carte.carte.reduction_pourcentage}%)."
                )
                # Forcer la sauvegarde de la session pour les messages
                request.session.modified = True
                return redirect('accounts:profil')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de la carte : {str(e)}")
                if settings.DEBUG:
                    import traceback
                    print(f"Erreur détaillée: {traceback.format_exc()}")
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
    else:
        form = CarteReductionForm()
    
    return render(request, 'accounts/ajouter_carte_reduction.html', {'form': form})


@login_required
def supprimer_carte_reduction(request, carte_id):
    """Supprimer une carte de réduction"""
    carte = CarteReductionUtilisateur.objects.filter(id=carte_id, utilisateur=request.user).first()
    if carte:
        carte.delete()
        messages.success(request, "Carte de réduction supprimée.")
    else:
        messages.error(request, "Carte de réduction introuvable.")
    return redirect('accounts:profil')


@login_required
def supprimer_compte(request):
    """Supprimer le compte utilisateur"""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect('reservations:home')
    
    return render(request, 'accounts/supprimer_compte.html')

