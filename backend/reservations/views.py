from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import translation
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse
from urllib.parse import urlencode
from datetime import date, datetime, timedelta
from decimal import Decimal
import secrets
import string
import json
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Train,
    Gare,
    Reservation,
    Passager,
    CarteReductionUtilisateur,
    OffrePromotion,
    RetardTrain,
    MaintenanceTrain,
)
from .forms import (
    RechercheTrainForm,
    FiltreTrainForm,
    ReservationForm,
    PassagerForm,
    PaiementForm,
    GestionReservationForm,
    AnnulationReservationForm,
    ReprogrammationReservationForm,
    RetardTrainForm,
    MaintenanceTrainForm,
)
from .utils import generer_billet_pdf, envoyer_billet_email, envoyer_notif_retard


def get_cart_count(request):
    """Retourne le nombre d'éléments dans le panier"""
    cart = request.session.get('cart', [])
    return len(cart)


def home(request):
    """Page d'accueil avec formulaire de recherche"""
    form = RechercheTrainForm()
    offres = OffrePromotion.objects.filter(actif=True, date_debut__lte=date.today(), date_fin__gte=date.today())[:3]
    
    if request.method == 'POST':
        form = RechercheTrainForm(request.POST)
        if form.is_valid():
            heure_depart = form.cleaned_data.get('heure_depart')
            date_retour = form.cleaned_data.get('date_retour')
            nombre_voyageurs = form.cleaned_data.get('nombre_voyageurs')

            if date_retour:
                request.session['date_retour'] = date_retour.isoformat()
            elif 'date_retour' in request.session:
                del request.session['date_retour']

            request.session['nombre_voyageurs'] = nombre_voyageurs
            gare_intermediaire_id = form.cleaned_data.get('gare_intermediaire')
            gare_inter_id_str = str(gare_intermediaire_id.id) if gare_intermediaire_id else '0'
            
            if heure_depart:
                return redirect('reservations:recherche_resultats_heure', 
                             gare_depart_id=form.cleaned_data['gare_depart'].id,
                             gare_arrivee_id=form.cleaned_data['gare_arrivee'].id,
                             date_depart=form.cleaned_data['date_depart'].strftime('%Y-%m-%d'),
                             heure_depart=heure_depart.strftime('%H:%M'),
                             gare_intermediaire_id=gare_inter_id_str)
            else:
                return redirect('reservations:recherche_resultats', 
                             gare_depart_id=form.cleaned_data['gare_depart'].id,
                             gare_arrivee_id=form.cleaned_data['gare_arrivee'].id,
                             date_depart=form.cleaned_data['date_depart'].strftime('%Y-%m-%d'),
                             gare_intermediaire_id=gare_inter_id_str)
    
    context = {
        'form': form,
        'offres': offres,
    }
    return render(request, 'reservations/home.html', context)


def gerer_reservation_public(request):
    """Permet à un utilisateur de retrouver et gérer un billet sans se connecter"""
    # Nettoyer le flag de téléchargement si demandé
    if request.GET.get('clear_download') == '1':
        if 'telecharger_billet_modifie' in request.session:
            del request.session['telecharger_billet_modifie']
            request.session.modified = True
    
    gestion_form = GestionReservationForm()
    reservation = None
    reschedule_form = None
    annulation_form = None
    email_recherche = None
    action = None
    modification_reussie = False  # Flag pour indiquer si une modification a été effectuée
    
    # Si des paramètres GET sont fournis (après redirection), rechercher la réservation
    if request.method == 'GET' and request.GET.get('code') and request.GET.get('email'):
        code_reservation = request.GET.get('code')
        email_recherche = request.GET.get('email')
        reservation = Reservation.objects.select_related(
            'train',
            'train__gare_depart',
            'train__gare_arrivee',
            'utilisateur'
        ).filter(
            code_reservation__iexact=code_reservation,
            utilisateur__email__iexact=email_recherche
        ).first()
        
        if reservation:
            gestion_form = GestionReservationForm(initial={
                'code_reservation': reservation.code_reservation,
                'email': email_recherche,
            })
            annulation_form = AnnulationReservationForm(initial={
                'reservation_id': reservation.id,
                'code_reservation': reservation.code_reservation,
                'email': email_recherche,
            })
            reschedule_form = ReprogrammationReservationForm(
                reservation=reservation,
                initial={
                    'reservation_id': reservation.id,
                    'code_reservation': reservation.code_reservation,
                    'email': email_recherche,
                    'nouvelle_date': reservation.date_voyage,
                    'nouveau_train': reservation.train_id,
                }
            )

    if request.method == 'POST':
        action = request.POST.get('action', 'rechercher')

        if action == 'rechercher':
            gestion_form = GestionReservationForm(request.POST)
            if gestion_form.is_valid():
                email_recherche = gestion_form.cleaned_data['email']
                reservation = Reservation.objects.select_related(
                    'train',
                    'train__gare_depart',
                    'train__gare_arrivee',
                    'utilisateur'
                ).filter(
                    code_reservation__iexact=gestion_form.cleaned_data['code_reservation'],
                    utilisateur__email__iexact=email_recherche
                ).first()

                if reservation:
                    annulation_form = AnnulationReservationForm(initial={
                        'reservation_id': reservation.id,
                        'code_reservation': reservation.code_reservation,
                        'email': email_recherche,
                    })
                    reschedule_form = ReprogrammationReservationForm(
                        reservation=reservation,
                        initial={
                            'reservation_id': reservation.id,
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                            'nouvelle_date': reservation.date_voyage,
                            'nouveau_train': reservation.train_id,
                        }
                    )
                else:
                    gestion_form.add_error(None, "Aucune réservation ne correspond à ces informations.")

        elif action == 'annuler':
            annulation_form = AnnulationReservationForm(request.POST)
            if annulation_form.is_valid():
                email_recherche = annulation_form.cleaned_data['email']
                reservation = Reservation.objects.select_related('train', 'utilisateur').filter(
                    id=annulation_form.cleaned_data['reservation_id'],
                    code_reservation__iexact=annulation_form.cleaned_data['code_reservation'],
                    utilisateur__email__iexact=email_recherche
                ).first()

                if not reservation:
                    messages.error(request, "Réservation introuvable.")
                elif reservation.statut == 'annulee':
                    messages.warning(request, "Cette réservation a déjà été annulée.")
                elif reservation.statut == 'utilisee':
                    messages.error(request, "Impossible d'annuler un billet déjà utilisé.")
                else:
                    reservation.statut = 'annulee'
                    reservation.save()
                    reservation.train.places_disponibles += reservation.nombre_places
                    reservation.train.save()
                    messages.success(request, "Votre réservation a été annulée. Un email de confirmation vous sera envoyé.")

        elif action == 'modifier':
            print("DEBUG: Action 'modifier' détectée")
            print(f"DEBUG: POST data: {request.POST}")
            # Récupérer d'abord la réservation pour pouvoir créer le formulaire correctement
            reservation_id = request.POST.get('reservation_id')
            email_recherche = request.POST.get('email', '')
            reservation = None
            if reservation_id:
                try:
                    reservation = Reservation.objects.select_related(
                        'train',
                        'train__gare_depart',
                        'train__gare_arrivee',
                        'utilisateur'
                    ).get(id=reservation_id)
                    print(f"DEBUG: Réservation trouvée pour créer le formulaire: {reservation.code_reservation}")
                except Reservation.DoesNotExist:
                    print("DEBUG: Réservation non trouvée avec l'ID fourni")
                    pass
            
            # Créer le formulaire avec la réservation si disponible
            if reservation:
                reschedule_form = ReprogrammationReservationForm(
                    reservation=reservation,
                    data=request.POST
                )
            else:
                reschedule_form = ReprogrammationReservationForm(request.POST)
            
            # Si le formulaire n'est pas valide, essayer de récupérer la réservation pour afficher les erreurs
            if not reschedule_form.is_valid():
                print(f"DEBUG: Formulaire invalide: {reschedule_form.errors}")
                print(f"DEBUG: Formulaire non valide, retour sans flags")
                if not reservation and reservation_id:
                    try:
                        reservation = Reservation.objects.select_related(
                            'train',
                            'train__gare_depart',
                            'train__gare_arrivee',
                            'utilisateur'
                        ).get(id=reservation_id)
                        gestion_form = GestionReservationForm(initial={
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        annulation_form = AnnulationReservationForm(initial={
                            'reservation_id': reservation.id,
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        reschedule_form = ReprogrammationReservationForm(
                            reservation=reservation,
                            data=request.POST
                        )
                        context = {
                            'gestion_form': gestion_form,
                            'reservation': reservation,
                            'reschedule_form': reschedule_form,
                            'annulation_form': annulation_form,
                            'email_recherche': email_recherche,
                        }
                        return render(request, 'reservations/gerer_reservation.html', context)
                    except Reservation.DoesNotExist:
                        pass
            if reschedule_form.is_valid():
                print("DEBUG: Formulaire de modification est VALIDE")
                email_recherche = reschedule_form.cleaned_data['email']
                reservation = Reservation.objects.select_related('train', 'utilisateur').filter(
                    id=reschedule_form.cleaned_data['reservation_id'],
                    code_reservation__iexact=reschedule_form.cleaned_data['code_reservation'],
                    utilisateur__email__iexact=email_recherche
                ).first()
                print(f"DEBUG: Réservation trouvée: {reservation is not None}")

                if not reservation:
                    messages.error(request, "Réservation introuvable.")
                    # Recharger la réservation si elle existe avec le code et l'email
                    reservation = Reservation.objects.select_related(
                        'train',
                        'train__gare_depart',
                        'train__gare_arrivee',
                        'utilisateur'
                    ).filter(
                        code_reservation__iexact=reschedule_form.cleaned_data['code_reservation'],
                        utilisateur__email__iexact=email_recherche
                    ).first()
                    if reservation:
                        gestion_form = GestionReservationForm(initial={
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        annulation_form = AnnulationReservationForm(initial={
                            'reservation_id': reservation.id,
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        reschedule_form = ReprogrammationReservationForm(
                            reservation=reservation,
                            initial={
                                'reservation_id': reservation.id,
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                                'nouvelle_date': reservation.date_voyage,
                                'nouveau_train': reservation.train_id,
                            }
                        )
                        context = {
                            'gestion_form': gestion_form,
                            'reservation': reservation,
                            'reschedule_form': reschedule_form,
                            'annulation_form': annulation_form,
                            'email_recherche': email_recherche,
                        }
                        return render(request, 'reservations/gerer_reservation.html', context)
                elif reservation.statut == 'annulee':
                    print(f"DEBUG: Réservation annulée, retour sans flags")
                    messages.error(request, "Cette réservation a été annulée et ne peut plus être modifiée.")
                    # Afficher quand même la réservation
                    reservation = Reservation.objects.select_related(
                        'train',
                        'train__gare_depart',
                        'train__gare_arrivee',
                        'utilisateur'
                    ).get(id=reservation.id)
                    gestion_form = GestionReservationForm(initial={
                        'code_reservation': reservation.code_reservation,
                        'email': email_recherche,
                    })
                    annulation_form = AnnulationReservationForm(initial={
                        'reservation_id': reservation.id,
                        'code_reservation': reservation.code_reservation,
                        'email': email_recherche,
                    })
                    reschedule_form = ReprogrammationReservationForm(
                        reservation=reservation,
                        initial={
                            'reservation_id': reservation.id,
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                            'nouvelle_date': reservation.date_voyage,
                            'nouveau_train': reservation.train_id,
                        }
                    )
                    context = {
                        'gestion_form': gestion_form,
                        'reservation': reservation,
                        'reschedule_form': reschedule_form,
                        'annulation_form': annulation_form,
                        'email_recherche': email_recherche,
                    }
                    return render(request, 'reservations/gerer_reservation.html', context)
                else:
                    nouveau_train = reschedule_form.cleaned_data['nouveau_train']
                    nouvelle_date = reschedule_form.cleaned_data['nouvelle_date']

                    if nouveau_train.places_disponibles < reservation.nombre_places and nouveau_train != reservation.train:
                        print(f"DEBUG: Pas assez de places disponibles, retour sans flags")
                        messages.error(request, "Le train sélectionné n'a pas assez de places disponibles.")
                        # Recharger la réservation et afficher la page
                        reservation = Reservation.objects.select_related(
                            'train',
                            'train__gare_depart',
                            'train__gare_arrivee',
                            'utilisateur'
                        ).get(id=reservation.id)
                        gestion_form = GestionReservationForm(initial={
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        annulation_form = AnnulationReservationForm(initial={
                            'reservation_id': reservation.id,
                            'code_reservation': reservation.code_reservation,
                            'email': email_recherche,
                        })
                        reschedule_form = ReprogrammationReservationForm(
                            reservation=reservation,
                            initial={
                                'reservation_id': reservation.id,
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                                'nouvelle_date': reservation.date_voyage,
                                'nouveau_train': reservation.train_id,
                            }
                        )
                        context = {
                            'gestion_form': gestion_form,
                            'reservation': reservation,
                            'reschedule_form': reschedule_form,
                            'annulation_form': annulation_form,
                            'email_recherche': email_recherche,
                        }
                        return render(request, 'reservations/gerer_reservation.html', context)
                    else:
                        print("DEBUG: Début de la modification de la réservation")
                        print(f"DEBUG: Nouveau train: {reschedule_form.cleaned_data['nouveau_train']}")
                        print(f"DEBUG: Nouvelle date: {reschedule_form.cleaned_data['nouvelle_date']}")
                        ancien_train = reservation.train
                        
                        # Annuler l'ancienne réservation
                        ancienne_reservation = reservation
                        ancienne_reservation.statut = 'annulee'
                        ancienne_reservation.save()
                        print(f"DEBUG: Ancienne réservation annulée: {ancienne_reservation.code_reservation}")
                        
                        # Remettre les places disponibles pour l'ancien train
                        if ancien_train != nouveau_train:
                            ancien_train.places_disponibles += ancienne_reservation.nombre_places
                            ancien_train.save()
                        # Si c'est le même train, on ne change pas les places (elles restent réservées)
                        
                        # Créer une nouvelle réservation avec le nouveau train et la nouvelle date
                        nouveau_code_reservation = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                        # S'assurer que le code est unique
                        while Reservation.objects.filter(code_reservation=nouveau_code_reservation).exists():
                            nouveau_code_reservation = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                        
                        print(f"DEBUG: Création d'une nouvelle réservation avec le code: {nouveau_code_reservation}")
                        nouvelle_reservation = Reservation.objects.create(
                            utilisateur=ancienne_reservation.utilisateur,
                            train=nouveau_train,
                            date_voyage=nouvelle_date,
                            nombre_places=ancienne_reservation.nombre_places,
                            carte_reduction=ancienne_reservation.carte_reduction,
                            prix_unitaire=ancienne_reservation.prix_unitaire,
                            reduction_appliquee=ancienne_reservation.reduction_appliquee,
                            prix_total=ancienne_reservation.prix_total,
                            statut='confirmee',
                            mode_paiement=ancienne_reservation.mode_paiement,
                            date_paiement=ancienne_reservation.date_paiement,
                            code_reservation=nouveau_code_reservation,
                        )
                        
                        # Réduire les places disponibles pour le nouveau train
                        nouveau_train.places_disponibles -= nouvelle_reservation.nombre_places
                        nouveau_train.save()
                        print(f"DEBUG: Places réduites pour le nouveau train")
                        
                        # Recharger la nouvelle réservation avec toutes les relations
                        nouvelle_reservation = Reservation.objects.select_related(
                            'train',
                            'train__gare_depart',
                            'train__gare_arrivee',
                            'utilisateur'
                        ).get(id=nouvelle_reservation.id)
                        print(f"DEBUG: Nouvelle réservation rechargée: {nouvelle_reservation.code_reservation}")
                        
                        # Générer et envoyer le nouveau billet
                        try:
                            print("DEBUG: Génération du PDF...")
                            pdf_path = generer_billet_pdf(nouvelle_reservation)
                            print("DEBUG: Envoi de l'email...")
                            envoyer_billet_email(nouvelle_reservation, pdf_path, est_modification=True)
                            print("DEBUG: Email envoyé avec succès")
                            messages.success(
                                request, 
                                f"Votre réservation a été modifiée avec succès. L'ancien billet a été annulé. "
                                f"Le nouveau billet (code: {nouvelle_reservation.code_reservation}) a été envoyé à {nouvelle_reservation.utilisateur.email} et est disponible au téléchargement."
                            )
                            # Stocker le code de la nouvelle réservation pour l'affichage
                            request.session['telecharger_billet_modifie'] = nouvelle_reservation.code_reservation
                            request.session.modified = True
                            print(f"DEBUG: Session mise à jour avec telecharger_billet_modifie = {nouvelle_reservation.code_reservation}")
                            
                            # Utiliser la nouvelle réservation pour l'affichage
                            reservation = nouvelle_reservation
                            
                            # Préparer les formulaires avec les nouvelles données
                            annulation_form = AnnulationReservationForm(initial={
                                'reservation_id': reservation.id,
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                            })
                            reschedule_form = ReprogrammationReservationForm(
                                reservation=reservation,
                                initial={
                                    'reservation_id': reservation.id,
                                    'code_reservation': reservation.code_reservation,
                                    'email': email_recherche,
                                    'nouvelle_date': reservation.date_voyage,
                                    'nouveau_train': reservation.train_id,
                                }
                            )
                            gestion_form = GestionReservationForm(initial={
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                            })
                            
                            # Afficher directement la page avec les nouvelles données (pas de redirection)
                            modification_reussie = True
                            # S'assurer que la session est bien sauvegardée
                            request.session.save()
                            # Passer explicitement le flag dans le contexte pour le template
                            # DEBUG: Vérifier que le flag est bien défini
                            print(f"DEBUG: billet_modifie sera True dans le contexte")
                            print(f"DEBUG: nouvelle_reservation.code_reservation = {nouvelle_reservation.code_reservation}")
                            print(f"DEBUG: reservation.code_reservation = {reservation.code_reservation}")
                            print(f"DEBUG: email_recherche = {email_recherche}")
                            context = {
                                'gestion_form': gestion_form,
                                'reservation': reservation,
                                'reschedule_form': reschedule_form,
                                'annulation_form': annulation_form,
                                'email_recherche': email_recherche,
                                'billet_modifie': True,  # Flag explicite pour afficher le nouveau billet
                                'nouveau_billet_code': nouvelle_reservation.code_reservation,  # Code du nouveau billet
                                'show_new_ticket': True,  # Flag supplémentaire pour garantir l'affichage
                            }
                            print(f"DEBUG: Contexte préparé avec billet_modifie=True, show_new_ticket=True")
                            print(f"DEBUG: Rendering template avec reservation.code_reservation = {reservation.code_reservation}")
                            return render(request, 'reservations/gerer_reservation.html', context)
                        except Exception as e:
                            import traceback
                            print(f"Erreur lors de l'envoi du billet: {str(e)}")
                            print(traceback.format_exc())
                            messages.warning(
                                request, 
                                f"Nouvelle réservation créée (code: {nouvelle_reservation.code_reservation}), mais erreur lors de l'envoi du billet : {str(e)}. "
                                "Vous pouvez télécharger le billet depuis la page de détails."
                            )
                            # Stocker le code de la nouvelle réservation même en cas d'erreur
                            request.session['telecharger_billet_modifie'] = nouvelle_reservation.code_reservation
                            request.session.modified = True
                            
                            # Utiliser la nouvelle réservation pour l'affichage
                            reservation = nouvelle_reservation
                            
                            # Préparer les formulaires même en cas d'erreur
                            annulation_form = AnnulationReservationForm(initial={
                                'reservation_id': reservation.id,
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                            })
                            reschedule_form = ReprogrammationReservationForm(
                                reservation=reservation,
                                initial={
                                    'reservation_id': reservation.id,
                                    'code_reservation': reservation.code_reservation,
                                    'email': email_recherche,
                                    'nouvelle_date': reservation.date_voyage,
                                    'nouveau_train': reservation.train_id,
                                }
                            )
                            gestion_form = GestionReservationForm(initial={
                                'code_reservation': reservation.code_reservation,
                                'email': email_recherche,
                            })
                            
                            modification_reussie = True
                            print(f"DEBUG: Contexte préparé avec billet_modifie=True, show_new_ticket=True (erreur)")
                            context = {
                                'gestion_form': gestion_form,
                                'reservation': reservation,
                                'reschedule_form': reschedule_form,
                                'annulation_form': annulation_form,
                                'email_recherche': email_recherche,
                                'billet_modifie': True,  # Flag explicite même en cas d'erreur
                                'show_new_ticket': True,  # Flag supplémentaire pour garantir l'affichage
                            }
                            return render(request, 'reservations/gerer_reservation.html', context)

        # Après une action autre que recherche, recharger la réservation pour afficher les infos actualisées
        # Ne pas exécuter si une modification a déjà été effectuée (déjà retourné)
        if action in ['annuler', 'modifier'] and reservation and not modification_reussie:
            # S'assurer que la réservation est bien rechargée avec toutes les relations
            reservation = Reservation.objects.select_related(
                'train',
                'train__gare_depart',
                'train__gare_arrivee',
                'utilisateur'
            ).get(id=reservation.id)
            annulation_form = AnnulationReservationForm(initial={
                'reservation_id': reservation.id,
                'code_reservation': reservation.code_reservation,
                'email': email_recherche,
            })
            reschedule_form = ReprogrammationReservationForm(
                reservation=reservation,
                initial={
                    'reservation_id': reservation.id,
                    'code_reservation': reservation.code_reservation,
                    'email': email_recherche,
                    'nouvelle_date': reservation.date_voyage,
                    'nouveau_train': reservation.train_id,
                }
            )

    context = {
        'gestion_form': gestion_form,
        'reservation': reservation,
        'reschedule_form': reschedule_form,
        'annulation_form': annulation_form,
        'email_recherche': email_recherche,
    }
    return render(request, 'reservations/gerer_reservation.html', context)


def recherche_resultats(request, gare_depart_id, gare_arrivee_id, date_depart, heure_depart='', gare_intermediaire_id=0):
    """Affiche les résultats de recherche de trains avec support des gares intermédiaires"""
    from .models import ArretIntermediaire
    
    gare_depart = get_object_or_404(Gare, id=gare_depart_id)
    gare_arrivee = get_object_or_404(Gare, id=gare_arrivee_id)
    gare_intermediaire = None
    if gare_intermediaire_id and gare_intermediaire_id != 0:
        try:
            gare_intermediaire = Gare.objects.get(id=gare_intermediaire_id)
        except Gare.DoesNotExist:
            gare_intermediaire = None
    
    # Gérer la modification de date/heure via POST
    if request.method == 'POST':
        nouvelle_date = request.POST.get('date_depart')
        nouvelle_heure = request.POST.get('heure_depart', '')
        gare_inter_id = request.POST.get('gare_intermediaire_id', gare_intermediaire_id)
        
        if nouvelle_date:
            if nouvelle_heure:
                return redirect('reservations:recherche_resultats_heure',
                             gare_depart_id=gare_depart_id,
                             gare_arrivee_id=gare_arrivee_id,
                             date_depart=nouvelle_date,
                             heure_depart=nouvelle_heure,
                             gare_intermediaire_id=gare_inter_id)
            else:
                return redirect('reservations:recherche_resultats',
                             gare_depart_id=gare_depart_id,
                             gare_arrivee_id=gare_arrivee_id,
                             date_depart=nouvelle_date,
                             gare_intermediaire_id=gare_inter_id)
    
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
    
    # Recherche des trains - deux cas :
    # 1. Trains directs (départ -> arrivée)
    # 2. Trains passant par une gare intermédiaire entre départ et arrivée
    trains_directs = Train.objects.filter(
        gare_depart=gare_depart,
        gare_arrivee=gare_arrivee,
        actif=True
    )
    
    # Si une gare intermédiaire est spécifiée, chercher aussi les trains qui passent par cette gare
    trains_via_intermediaire = Train.objects.none()
    if gare_intermediaire:
        # Trains qui partent de gare_depart, arrivent à gare_arrivee, et passent par gare_intermediaire
        trains_via_intermediaire = Train.objects.filter(
            gare_depart=gare_depart,
            gare_arrivee=gare_arrivee,
            arrets_intermediaires__gare=gare_intermediaire,
            actif=True
        ).distinct()
        
        # Vérifier que la gare intermédiaire est bien entre le départ et l'arrivée
        trains_valides = []
        for train in trains_via_intermediaire:
            if train.gare_est_entre_depart_et_arrivee(gare_intermediaire, gare_depart, gare_arrivee):
                trains_valides.append(train.id)
        trains_via_intermediaire = Train.objects.filter(id__in=trains_valides)
    
    # Combiner les deux querysets
    trains = (trains_directs | trains_via_intermediaire).distinct()
    
    # Exclure les trains en maintenance
    trains = trains.exclude(
        maintenances__date_debut__lte=date_depart_obj,
        maintenances__date_fin__gte=date_depart_obj,
        maintenances__statut__in=['planifie', 'en_cours']
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
        'gare_intermediaire': gare_intermediaire,
        'gare_intermediaire_id': gare_intermediaire_id,
        'date_depart': date_depart_obj,
        'heure_depart': heure_depart_obj,
        'heure_depart_str': heure_depart,  # Pour l'affichage dans le formulaire
        'filtre_form': filtre_form,
        'date_aujourdhui': date.today(),  # Pour la validation dans le template
        'date_retour': request.session.get('date_retour'),
        'nombre_voyageurs': request.session.get('nombre_voyageurs', 1),
    }
    return render(request, 'reservations/recherche_resultats.html', context)


@login_required
def reserver_train(request, train_id):
    """Page de réservation d'un train - Ajoute au panier"""
    train = get_object_or_404(Train, id=train_id, actif=True)
    
    date_voyage_str = request.session.get('date_voyage')
    try:
        date_voyage = datetime.strptime(date_voyage_str, '%Y-%m-%d').date() if date_voyage_str else date.today()
    except ValueError:
        date_voyage = date.today()

    if train.est_en_maintenance(date_voyage):
        messages.error(request, "Ce train est indisponible à la date sélectionnée en raison d'une maintenance.")
        return redirect('reservations:home')

    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST, user=request.user)
        
        if reservation_form.is_valid():
            nombre_places = reservation_form.cleaned_data['nombre_places']
            carte_reduction = reservation_form.cleaned_data.get('carte_reduction')
            
            # Vérifier les places disponibles
            if train.places_disponibles < nombre_places:
                messages.error(request, f"Seulement {train.places_disponibles} place(s) disponible(s).")
                return redirect('reservations:reserver_train', train_id=train_id)
            
            # Vérifier si la carte peut être utilisée aujourd'hui (max 2 fois par jour)
            if carte_reduction:
                if not carte_reduction.peut_utiliser_aujourdhui():
                    messages.warning(
                        request, 
                        f"Votre carte de réduction '{carte_reduction.carte.nom}' a déjà été utilisée 2 fois aujourd'hui. "
                        "La réduction ne sera pas appliquée pour cette réservation."
                    )
                    carte_reduction = None
            
            # Calculer le prix total
            prix_unitaire = train.prix_base
            prix_base_total = prix_unitaire * nombre_places
            reduction_appliquee = Decimal('0.00')
            prix_total = prix_base_total
            
            if carte_reduction:
                reduction_appliquee = prix_base_total * (carte_reduction.carte.reduction_pourcentage / 100)
                prix_total = prix_base_total - reduction_appliquee
            
            # Ajouter au panier (session)
            cart = request.session.get('cart', [])
            cart_item = {
                'train_id': train_id,
                'train_numero': train.numero,
                'gare_depart': train.gare_depart.nom,
                'gare_arrivee': train.gare_arrivee.nom,
                'heure_depart': train.heure_depart.strftime('%H:%M'),
                'heure_arrivee': train.heure_arrivee.strftime('%H:%M'),
                'date_voyage': str(date_voyage),
                'nombre_places': nombre_places,
                'carte_reduction_id': carte_reduction.id if carte_reduction else None,
                'prix_unitaire': str(prix_unitaire),
                'reduction_appliquee': str(reduction_appliquee),
                'prix_total': str(prix_total),
            }
            cart.append(cart_item)
            request.session['cart'] = cart
            request.session.modified = True
            
            messages.success(request, f"Réservation ajoutée au panier !")
            return redirect('reservations:panier')
    
    reservation_form = ReservationForm(user=request.user)
    
    # Stocker la date de voyage en session
    date_voyage_input = request.GET.get('date', date_voyage_str or str(date.today()))
    request.session['date_voyage'] = date_voyage_input
    
    # Préparer les informations des cartes pour le JavaScript
    cartes_info = {}
    if request.user.is_authenticated:
        cartes_disponibles = CarteReductionUtilisateur.objects.filter(
            utilisateur=request.user,
            date_expiration__gte=date.today()
        )
        for carte in cartes_disponibles:
            if carte.peut_utiliser_aujourdhui():
                cartes_info[carte.id] = {
                    'pourcentage': float(carte.carte.reduction_pourcentage),
                    'nom': carte.carte.nom
                }
    
    context = {
        'train': train,
        'reservation_form': reservation_form,
        'date_voyage': request.session.get('date_voyage', date.today()),
        'cartes_info_json': json.dumps(cartes_info),
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
    
    # Utiliser une approche différente pour éviter les problèmes de timezone avec TruncMonth
    # Récupérer toutes les réservations et grouper par mois en Python
    from collections import defaultdict
    reservations_par_mois_dict = defaultdict(int)
    
    for reservation in reservations:
        date_res = reservation.date_reservation
        # Convertir en naive si nécessaire
        if timezone.is_aware(date_res):
            date_res = timezone.make_naive(date_res)
        # Extraire année-mois
        mois_key = date_res.strftime('%Y-%m')
        reservations_par_mois_dict[mois_key] += 1
    
    # Trier par mois et formater pour le graphique
    chart_labels = []
    chart_values = []
    for mois_key in sorted(reservations_par_mois_dict.keys()):
        # Convertir '2024-11' en 'Nov 2024'
        try:
            annee, mois = mois_key.split('-')
            mois_int = int(mois)
            mois_nom = date(2000, mois_int, 1).strftime('%b')
            chart_labels.append(f'{mois_nom} {annee}')
        except:
            chart_labels.append(mois_key)
        chart_values.append(reservations_par_mois_dict[mois_key])

    retard_stats = (
        RetardTrain.objects.filter(train__reservations__utilisateur=request.user)
        .values('train__numero')
        .annotate(total=Count('id', distinct=True))
        .order_by('train__numero')
    )
    retard_labels = [entry['train__numero'] for entry in retard_stats]
    retard_values = [entry['total'] for entry in retard_stats]

    retards_recents = RetardTrain.objects.filter(
        train__reservations__utilisateur=request.user
    ).select_related('train').distinct()[:5]
    
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
        'chart_data': json.dumps({
            'labels': chart_labels,
            'datasets': [{
                'label': 'Réservations confirmées',
                'data': chart_values,
                'borderColor': '#ff6600',
                'backgroundColor': 'rgba(255,102,0,0.1)',
                'tension': 0.4,
            }]
        }),
        'retard_chart_data': json.dumps({
            'labels': retard_labels,
            'datasets': [{
                'label': 'Retards signalés',
                'data': retard_values,
                'backgroundColor': 'rgba(255,99,132,0.6)',
            }]
        }),
        'retards_recents': retards_recents,
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
    retard = RetardTrain.objects.filter(train=reservation.train, date_voyage=reservation.date_voyage).first()
    maintenance = MaintenanceTrain.objects.filter(
        train=reservation.train,
        date_debut__lte=reservation.date_voyage,
        date_fin__gte=reservation.date_voyage
    ).exclude(statut='terminee').first()
    
    context = {
        'reservation': reservation,
        'retard': retard,
        'maintenance': maintenance,
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
    """Téléchargement du billet PDF (pour utilisateurs connectés)"""
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


def telecharger_billet_public(request, code):
    """Téléchargement du billet PDF (pour utilisateurs non connectés via code et email)"""
    email = request.GET.get('email', '')
    
    if not email:
        messages.error(request, "Email requis pour télécharger le billet.")
        return redirect('reservations:gerer_reservation')
    
    reservation = Reservation.objects.filter(
        code_reservation=code,
        utilisateur__email__iexact=email
    ).first()
    
    if not reservation:
        messages.error(request, "Réservation introuvable ou email incorrect.")
        return redirect('reservations:gerer_reservation')
    
    if reservation.statut != 'confirmee':
        messages.error(request, "Cette réservation n'est pas confirmée.")
        return redirect('reservations:gerer_reservation')
    
    try:
        pdf_path = generer_billet_pdf(reservation)
        with open(pdf_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="billet_{reservation.code_reservation}.pdf"'
            return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du billet : {str(e)}")
        return redirect('reservations:gerer_reservation')


@staff_member_required
def gestion_retards(request):
    """Liste et création des retards"""
    retards = RetardTrain.objects.select_related('train').order_by('-date_voyage')
    form = RetardTrainForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            retard = form.save()
            reservations_concernees = Reservation.objects.filter(
                train=retard.train,
                date_voyage=retard.date_voyage,
                statut='confirmee'
            ).select_related('utilisateur', 'train', 'train__gare_depart', 'train__gare_arrivee')
            envoyer_notif_retard(retard, reservations_concernees)
            messages.success(request, "Retard enregistré avec succès.")
            return redirect('reservations:gestion_retards')

    context = {
        'retards': retards,
        'form': form,
    }
    return render(request, 'reservations/retards.html', context)


@staff_member_required
def gestion_maintenance(request):
    """Module de maintenance des trains"""
    maintenances = MaintenanceTrain.objects.select_related('train').order_by('-date_debut')
    form = MaintenanceTrainForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Maintenance enregistrée avec succès.")
            return redirect('reservations:gestion_maintenance')

    context = {
        'maintenances': maintenances,
        'form': form,
    }
    return render(request, 'reservations/maintenance.html', context)


def offres_promotions(request):
    """Page des offres et promotions"""
    offres = OffrePromotion.objects.filter(actif=True).order_by('-date_debut')
    
    # Filtrer les offres valides
    offres_valides = [offre for offre in offres if offre.est_valide()]
    
    context = {
        'offres': offres_valides,
    }
    return render(request, 'reservations/offres_promotions.html', context)


@require_POST
def change_language_ajax(request):
    """Change la langue via AJAX sans rechargement de page"""
    lang = request.POST.get('language', 'fr')
    if lang in ['fr', 'en']:
        translation.activate(lang)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
        request.session.modified = True
        # Activer la langue pour cette requête
        response = JsonResponse({'success': True, 'language': lang})
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    return JsonResponse({'success': False, 'error': 'Invalid language'}, status=400)


@login_required
def panier(request):
    """Affiche le panier de réservations"""
    cart = request.session.get('cart', [])
    cart_items = []
    total = Decimal('0.00')
    
    for item in cart:
        train = get_object_or_404(Train, id=item['train_id'])
        cart_items.append({
            'index': len(cart_items),
            'train': train,
            'date_voyage': item['date_voyage'],
            'nombre_places': item['nombre_places'],
            'prix_total': Decimal(item['prix_total']),
            'carte_reduction_id': item.get('carte_reduction_id'),
        })
        total += Decimal(item['prix_total'])
    
    if request.method == 'POST':
        if 'supprimer' in request.POST:
            index = int(request.POST.get('index'))
            cart = request.session.get('cart', [])
            if 0 <= index < len(cart):
                cart.pop(index)
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, "Réservation retirée du panier.")
            return redirect('reservations:panier')
        
        elif 'finaliser' in request.POST:
            # Créer les réservations depuis le panier
            cart = request.session.get('cart', [])
            if not cart:
                messages.error(request, "Votre panier est vide.")
                return redirect('reservations:panier')
            
            # Créer toutes les réservations
            reservation_ids = []
            for item in cart:
                train = get_object_or_404(Train, id=item['train_id'])
                date_voyage = datetime.strptime(item['date_voyage'], '%Y-%m-%d').date()
                
                # Vérifier les places disponibles
                if train.places_disponibles < item['nombre_places']:
                    messages.error(request, f"Plus assez de places disponibles pour {train.nom}.")
                    continue
                
                code_reservation = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                carte_reduction = None
                reduction_appliquee = Decimal(item.get('reduction_appliquee', '0.00'))
                prix_total = Decimal(item['prix_total'])
                
                if item.get('carte_reduction_id'):
                    carte_reduction = CarteReductionUtilisateur.objects.filter(
                        id=item['carte_reduction_id'],
                        utilisateur=request.user
                    ).first()
                    
                    # Vérifier si la carte peut encore être utilisée aujourd'hui
                    if carte_reduction and not carte_reduction.peut_utiliser_aujourdhui():
                        # La carte a atteint sa limite, recalculer sans réduction
                        prix_unitaire = Decimal(item['prix_unitaire'])
                        prix_base_total = prix_unitaire * item['nombre_places']
                        reduction_appliquee = Decimal('0.00')
                        prix_total = prix_base_total
                        carte_reduction = None
                        messages.warning(
                            request,
                            f"La carte de réduction a atteint sa limite d'utilisation quotidienne (2 fois/jour). "
                            f"La réduction n'a pas été appliquée pour le train {train.numero}."
                        )
                
                reservation = Reservation.objects.create(
                    utilisateur=request.user,
                    train=train,
                    date_voyage=date_voyage,
                    nombre_places=item['nombre_places'],
                    carte_reduction=carte_reduction,
                    prix_unitaire=Decimal(item['prix_unitaire']),
                    reduction_appliquee=reduction_appliquee,
                    prix_total=prix_total,
                    code_reservation=code_reservation
                )
                reservation_ids.append(reservation.id)
            
            if reservation_ids:
                # Stocker la première réservation pour le paiement
                request.session['reservation_id'] = reservation_ids[0]
                request.session['reservation_ids'] = reservation_ids
                # Vider le panier
                request.session['cart'] = []
                request.session.modified = True
                messages.success(request, f"{len(reservation_ids)} réservation(s) créée(s). Procédez au paiement.")
                return redirect('reservations:paiement')
            else:
                messages.error(request, "Aucune réservation n'a pu être créée.")
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'reservations/panier.html', context)

