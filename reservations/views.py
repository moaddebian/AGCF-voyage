from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from datetime import date, datetime, timedelta
from decimal import Decimal
import secrets
import string

from .models import Train, Gare, Reservation, Passager, CarteReductionUtilisateur, OffrePromotion
from .forms import RechercheTrainForm, FiltreTrainForm, ReservationForm, PassagerForm, PaiementForm
from .utils import generer_billet_pdf, envoyer_billet_email


def home(request):
    """Page d'accueil avec formulaire de recherche"""
    form = RechercheTrainForm()
    offres = OffrePromotion.objects.filter(actif=True, date_debut__lte=date.today(), date_fin__gte=date.today())[:3]
    
    if request.method == 'POST':
        form = RechercheTrainForm(request.POST)
        if form.is_valid():
            heure_depart = form.cleaned_data.get('heure_depart')
            if heure_depart:
                return redirect('reservations:recherche_resultats_heure', 
                             gare_depart_id=form.cleaned_data['gare_depart'].id,
                             gare_arrivee_id=form.cleaned_data['gare_arrivee'].id,
                             date_depart=form.cleaned_data['date_depart'].strftime('%Y-%m-%d'),
                             heure_depart=heure_depart.strftime('%H:%M'))
            else:
                return redirect('reservations:recherche_resultats', 
                             gare_depart_id=form.cleaned_data['gare_depart'].id,
                             gare_arrivee_id=form.cleaned_data['gare_arrivee'].id,
                             date_depart=form.cleaned_data['date_depart'].strftime('%Y-%m-%d'))
    
    context = {
        'form': form,
        'offres': offres,
    }
    return render(request, 'reservations/home.html', context)


def recherche_resultats(request, gare_depart_id, gare_arrivee_id, date_depart, heure_depart=''):
    """Affiche les résultats de recherche de trains"""
    gare_depart = get_object_or_404(Gare, id=gare_depart_id)
    gare_arrivee = get_object_or_404(Gare, id=gare_arrivee_id)
    
    # Gérer la modification de date/heure via POST
    if request.method == 'POST':
        nouvelle_date = request.POST.get('date_depart')
        nouvelle_heure = request.POST.get('heure_depart', '')
        
        if nouvelle_date:
            if nouvelle_heure:
                return redirect('reservations:recherche_resultats_heure',
                             gare_depart_id=gare_depart_id,
                             gare_arrivee_id=gare_arrivee_id,
                             date_depart=nouvelle_date,
                             heure_depart=nouvelle_heure)
            else:
                return redirect('reservations:recherche_resultats',
                             gare_depart_id=gare_depart_id,
                             gare_arrivee_id=gare_arrivee_id,
                             date_depart=nouvelle_date)
    
    try:
        date_depart_obj = datetime.strptime(date_depart, '%Y-%m-%d').date()
    except:
        date_depart_obj = date.today()
    
    # Convertir l'heure en objet time si fournie
    heure_depart_obj = None
    if heure_depart:
        try:
            heure_depart_obj = datetime.strptime(heure_depart, '%H:%M').time()
        except:
            pass
    
    # Recherche des trains
    trains = Train.objects.filter(
        gare_depart=gare_depart,
        gare_arrivee=gare_arrivee,
        actif=True
    )
    
    # Filtrage par heure si fournie
    if heure_depart_obj:
        trains = trains.filter(heure_depart__gte=heure_depart_obj)
    
    # Filtrage par formulaire
    filtre_form = FiltreTrainForm(request.GET)
    if filtre_form.is_valid():
        classe = filtre_form.cleaned_data.get('classe')
        prix_max = filtre_form.cleaned_data.get('prix_max')
        tri = filtre_form.cleaned_data.get('tri')
        
        if classe:
            trains = trains.filter(classe=classe)
        
        if prix_max:
            trains = trains.filter(prix_base__lte=prix_max)
        
        if tri == 'prix':
            trains = trains.order_by('prix_base')
        elif tri == 'duree':
            trains = trains.order_by('duree')
        else:
            trains = trains.order_by('heure_depart')
    else:
        trains = trains.order_by('heure_depart')
    
    # Pagination
    paginator = Paginator(trains, 10)
    page_number = request.GET.get('page')
    trains_page = paginator.get_page(page_number)
    
    context = {
        'trains': trains_page,
        'gare_depart': gare_depart,
        'gare_arrivee': gare_arrivee,
        'date_depart': date_depart_obj,
        'heure_depart': heure_depart_obj,
        'heure_depart_str': heure_depart,  # Pour l'affichage dans le formulaire
        'filtre_form': filtre_form,
        'date_aujourdhui': date.today(),  # Pour la validation dans le template
    }
    return render(request, 'reservations/recherche_resultats.html', context)


@login_required
def reserver_train(request, train_id):
    """Page de réservation d'un train"""
    train = get_object_or_404(Train, id=train_id, actif=True)
    
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST, user=request.user)
        
        if reservation_form.is_valid():
            nombre_places = reservation_form.cleaned_data['nombre_places']
            carte_reduction = reservation_form.cleaned_data.get('carte_reduction')
            
            # Vérifier les places disponibles
            if train.places_disponibles < nombre_places:
                messages.error(request, f"Seulement {train.places_disponibles} place(s) disponible(s).")
                return redirect('reservations:reserver_train', train_id=train_id)
            
            # Créer la réservation
            code_reservation = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Calculer le prix total avant de créer la réservation
            prix_unitaire = train.prix_base
            prix_base_total = prix_unitaire * nombre_places
            reduction_appliquee = Decimal('0.00')
            prix_total = prix_base_total
            
            if carte_reduction:
                reduction_appliquee = prix_base_total * (carte_reduction.carte.reduction_pourcentage / 100)
                prix_total = prix_base_total - reduction_appliquee
            
            reservation = Reservation.objects.create(
                utilisateur=request.user,
                train=train,
                date_voyage=request.session.get('date_voyage', date.today()),
                nombre_places=nombre_places,
                carte_reduction=carte_reduction,
                prix_unitaire=prix_unitaire,
                reduction_appliquee=reduction_appliquee,
                prix_total=prix_total,
                code_reservation=code_reservation
            )
            
            # Stocker l'ID de réservation en session
            request.session['reservation_id'] = reservation.id
            
            # Rediriger directement vers le paiement
            return redirect('reservations:paiement')
    
    reservation_form = ReservationForm(user=request.user)
    
    # Stocker la date de voyage en session
    date_voyage = request.GET.get('date', str(date.today()))
    request.session['date_voyage'] = date_voyage
    
    context = {
        'train': train,
        'reservation_form': reservation_form,
        'date_voyage': request.session.get('date_voyage', date.today()),
    }
    return render(request, 'reservations/reserver_train.html', context)


@login_required
def ajouter_passagers(request):
    """Ajout des informations des passagers"""
    reservation_id = request.session.get('reservation_id')
    if not reservation_id:
        messages.error(request, "Aucune réservation en cours.")
        return redirect('reservations:home')
    
    reservation = get_object_or_404(Reservation, id=reservation_id, utilisateur=request.user)
    
    if request.method == 'POST':
        forms = [PassagerForm(request.POST, prefix=str(i)) for i in range(reservation.nombre_places)]
        
        if all(form.is_valid() for form in forms):
            # Supprimer les anciens passagers
            reservation.passagers.all().delete()
            
            # Créer les nouveaux passagers
            for form in forms:
                Passager.objects.create(
                    reservation=reservation,
                    nom=form.cleaned_data['nom'],
                    prenom=form.cleaned_data['prenom'],
                    date_naissance=form.cleaned_data['date_naissance']
                )
            
            return redirect('reservations:paiement')
    else:
        forms = [PassagerForm(prefix=str(i)) for i in range(reservation.nombre_places)]
    
    context = {
        'reservation': reservation,
        'forms': forms,
    }
    return render(request, 'reservations/ajouter_passagers.html', context)


@login_required
def paiement(request):
    """Page de paiement"""
    reservation_id = request.session.get('reservation_id')
    if not reservation_id:
        messages.error(request, "Aucune réservation en cours.")
        return redirect('reservations:home')
    
    reservation = get_object_or_404(Reservation, id=reservation_id, utilisateur=request.user)
    
    if reservation.statut != 'en_attente':
        messages.warning(request, "Cette réservation a déjà été traitée.")
        return redirect('reservations:dashboard')
    
    if request.method == 'POST':
        paiement_form = PaiementForm(request.POST)
        
        if paiement_form.is_valid():
            # Créer les passagers automatiquement avec les infos de l'utilisateur si non créés
            if reservation.passagers.count() == 0:
                from .models import Passager
                from datetime import date as date_obj
                # Utiliser les infos de l'utilisateur pour créer les passagers
                for i in range(reservation.nombre_places):
                    Passager.objects.create(
                        reservation=reservation,
                        nom=request.user.last_name or 'Nom',
                        prenom=request.user.first_name or 'Prénom',
                        date_naissance=request.user.profil.date_naissance if hasattr(request.user, 'profil') and request.user.profil.date_naissance else date_obj(1990, 1, 1)
                    )
            
            # Simuler le paiement (dans un vrai projet, intégrer Stripe, PayPal, etc.)
            reservation.mode_paiement = paiement_form.cleaned_data['mode_paiement']
            reservation.statut = 'confirmee'
            reservation.date_paiement = timezone.now()
            reservation.save()
            
            # Mettre à jour les places disponibles
            reservation.train.places_disponibles -= reservation.nombre_places
            reservation.train.save()
            
            # Générer et envoyer le billet
            try:
                pdf_path = generer_billet_pdf(reservation)
                envoyer_billet_email(reservation, pdf_path)
                messages.success(request, f"Paiement effectué avec succès ! Votre billet a été envoyé par email.")
                
                # Stocker un flag pour déclencher le téléchargement automatique
                request.session['telecharger_billet'] = reservation.code_reservation
            except Exception as e:
                messages.warning(request, f"Paiement effectué, mais erreur lors de l'envoi du billet : {str(e)}")
            
            # Nettoyer la session
            if 'reservation_id' in request.session:
                del request.session['reservation_id']
            if 'date_voyage' in request.session:
                del request.session['date_voyage']
            
            return redirect('reservations:confirmation', code=reservation.code_reservation)
    
    paiement_form = PaiementForm()
    
    context = {
        'reservation': reservation,
        'paiement_form': paiement_form,
    }
    return render(request, 'reservations/paiement.html', context)


@login_required
def confirmation(request, code):
    """Page de confirmation de réservation"""
    reservation = get_object_or_404(Reservation, code_reservation=code, utilisateur=request.user)
    
    # Vérifier si le billet doit être téléchargé automatiquement
    telecharger_billet = request.session.pop('telecharger_billet', None)
    auto_download = (telecharger_billet == code)
    
    context = {
        'reservation': reservation,
        'auto_download': auto_download,
    }
    return render(request, 'reservations/confirmation.html', context)


@login_required
def dashboard(request):
    """Tableau de bord utilisateur"""
    reservations = Reservation.objects.filter(utilisateur=request.user).order_by('-date_reservation')
    
    # Statistiques
    stats = {
        'total': reservations.count(),
        'confirmees': reservations.filter(statut='confirmee').count(),
        'annulees': reservations.filter(statut='annulee').count(),
        'a_venir': reservations.filter(statut='confirmee', date_voyage__gte=date.today()).count(),
    }
    
    context = {
        'reservations': reservations[:10],  # Dernières 10 réservations
        'stats': stats,
    }
    return render(request, 'reservations/dashboard.html', context)


@login_required
def mes_reservations(request):
    """Liste complète des réservations"""
    reservations = Reservation.objects.filter(utilisateur=request.user).order_by('-date_reservation')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        reservations = reservations.filter(statut=statut)
    
    context = {
        'reservations': reservations,
        'statut_actuel': statut,
    }
    return render(request, 'reservations/mes_reservations.html', context)


@login_required
def detail_reservation(request, code):
    """Détails d'une réservation"""
    reservation = get_object_or_404(Reservation, code_reservation=code, utilisateur=request.user)
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/detail_reservation.html', context)


@login_required
def annuler_reservation(request, code):
    """Annulation d'une réservation"""
    reservation = get_object_or_404(Reservation, code_reservation=code, utilisateur=request.user)
    
    if reservation.statut == 'annulee':
        messages.warning(request, "Cette réservation est déjà annulée.")
        return redirect('reservations:detail_reservation', code=code)
    
    if reservation.statut == 'utilisee':
        messages.error(request, "Impossible d'annuler une réservation déjà utilisée.")
        return redirect('reservations:detail_reservation', code=code)
    
    if request.method == 'POST':
        reservation.statut = 'annulee'
        reservation.save()
        
        # Remettre les places disponibles
        reservation.train.places_disponibles += reservation.nombre_places
        reservation.train.save()
        
        messages.success(request, "Réservation annulée avec succès.")
        return redirect('reservations:detail_reservation', code=code)
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/annuler_reservation.html', context)


@login_required
def telecharger_billet(request, code):
    """Téléchargement du billet PDF"""
    reservation = get_object_or_404(Reservation, code_reservation=code, utilisateur=request.user)
    
    if reservation.statut != 'confirmee':
        messages.error(request, "Cette réservation n'est pas confirmée.")
        return redirect('reservations:detail_reservation', code=code)
    
    try:
        pdf_path = generer_billet_pdf(reservation)
        with open(pdf_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="billet_{reservation.code_reservation}.pdf"'
            return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du billet : {str(e)}")
        return redirect('reservations:detail_reservation', code=code)


def offres_promotions(request):
    """Page des offres et promotions"""
    offres = OffrePromotion.objects.filter(actif=True).order_by('-date_debut')
    
    # Filtrer les offres valides
    offres_valides = [offre for offre in offres if offre.est_valide()]
    
    context = {
        'offres': offres_valides,
    }
    return render(request, 'reservations/offres_promotions.html', context)

