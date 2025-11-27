from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Gare,
    Train,
    CarteReductionUtilisateur,
    Reservation,
    Passager,
    OffrePromotion,
    RetardTrain,
    MaintenanceTrain,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from datetime import date, datetime


class RechercheTrainForm(forms.Form):
    """Formulaire de recherche de trains"""
    gare_depart = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare de départ",
        empty_label="Ma gare de départ",
        widget=forms.Select(attrs={'class': 'form-select select-placeholder'})
    )
    gare_arrivee = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare d'arrivée",
        empty_label="Ma gare d'arrivée",
        widget=forms.Select(attrs={'class': 'form-select select-placeholder'})
    )
    gare_intermediaire = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare intermédiaire (optionnel)",
        required=False,
        empty_label="Aucune gare intermédiaire",
        widget=forms.Select(attrs={'class': 'form-select select-placeholder'}),
        help_text="Rechercher un train passant par cette gare entre le départ et l'arrivée"
    )
    date_depart = forms.DateField(
        label="Date de départ",
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control d-none actual-date-input',
            'data-role': 'date-input'
        })
    )
    heure_depart = forms.TimeField(
        label="Heure de départ (optionnel)",
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control d-none actual-time-input',
            'data-role': 'time-input'
        })
    )
    date_retour = forms.DateField(
        label="Date de retour",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Mon retour',
            'onfocus': "(this.type='date')",
            'onblur': "(this.type='text')"
        })
    )
    nombre_voyageurs = forms.IntegerField(
        label="Voyageurs",
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_str = date.today().isoformat()
        self.fields['date_depart'].widget.attrs['min'] = today_str
        if not self.data.get(self.add_prefix('date_depart')):
            self.fields['date_depart'].initial = date.today()
            self.fields['date_depart'].widget.attrs['value'] = today_str
        date_depart_value = self.data.get(self.add_prefix('date_depart')) or today_str
        self.fields['date_retour'].widget.attrs['min'] = date_depart_value
    
    def clean(self):
        cleaned_data = super().clean()
        gare_depart = cleaned_data.get('gare_depart')
        gare_arrivee = cleaned_data.get('gare_arrivee')
        gare_intermediaire = cleaned_data.get('gare_intermediaire')
        date_depart = cleaned_data.get('date_depart')
        
        if gare_depart and gare_arrivee:
            if gare_depart == gare_arrivee:
                raise forms.ValidationError("La gare de départ et d'arrivée doivent être différentes.")
            
            # Vérifier que la gare intermédiaire est différente du départ et de l'arrivée
            if gare_intermediaire:
                if gare_intermediaire == gare_depart:
                    raise forms.ValidationError("La gare intermédiaire doit être différente de la gare de départ.")
                if gare_intermediaire == gare_arrivee:
                    raise forms.ValidationError("La gare intermédiaire doit être différente de la gare d'arrivée.")
        
        if date_depart and date_depart < date.today():
            raise forms.ValidationError("La date de départ ne peut pas être dans le passé.")

        date_retour = cleaned_data.get('date_retour')
        if date_retour:
            if date_depart and date_retour < date_depart:
                raise forms.ValidationError("La date de retour doit être postérieure à la date de départ.")
            if date_retour < date.today():
                raise forms.ValidationError("La date de retour ne peut pas être dans le passé.")
        
        return cleaned_data


class FiltreTrainForm(forms.Form):
    """Formulaire de filtrage des résultats de recherche"""
    classe = forms.ChoiceField(
        choices=[('', 'Toutes les classes')] + Train.CLASSE_CHOICES,
        required=False,
        label="Classe",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    prix_max = forms.DecimalField(
        required=False,
        label="Prix maximum",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    tri = forms.ChoiceField(
        choices=[
            ('heure', 'Heure de départ'),
            ('prix', 'Prix croissant'),
            ('duree', 'Durée'),
        ],
        required=False,
        label="Trier par",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ReservationForm(forms.ModelForm):
    """Formulaire de réservation"""
    nombre_places = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        label="Nombre de places",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    carte_reduction = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Carte de réduction",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Reservation
        fields = ['nombre_places', 'carte_reduction']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtrer les cartes valides et utilisables aujourd'hui
            cartes_valides = CarteReductionUtilisateur.objects.filter(
                utilisateur=user,
                date_expiration__gte=date.today()
            )
            # Filtrer celles qui peuvent être utilisées aujourd'hui (max 2 fois)
            cartes_disponibles = [carte for carte in cartes_valides if carte.peut_utiliser_aujourdhui()]
            
            if cartes_disponibles:
                self.fields['carte_reduction'].queryset = CarteReductionUtilisateur.objects.filter(
                    id__in=[c.id for c in cartes_disponibles]
                )
                # Pré-sélectionner automatiquement la première carte disponible
                if not self.initial.get('carte_reduction') and not self.data:
                    self.initial['carte_reduction'] = cartes_disponibles[0]
            else:
                # Aucune carte disponible, queryset vide
                self.fields['carte_reduction'].queryset = CarteReductionUtilisateur.objects.none()


class PassagerForm(forms.ModelForm):
    """Formulaire pour les informations d'un passager"""
    class Meta:
        model = Passager
        fields = ['nom', 'prenom', 'date_naissance']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PaiementForm(forms.Form):
    """Formulaire de paiement"""
    MODE_PAIEMENT_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'PayPal'),
    ]
    
    mode_paiement = forms.ChoiceField(
        choices=MODE_PAIEMENT_CHOICES,
        label="Mode de paiement",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    numero_carte = forms.CharField(
        max_length=19,
        required=False,
        label="Numéro de carte",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456'})
    )
    date_expiration = forms.CharField(
        max_length=5,
        required=False,
        label="Date d'expiration (MM/AA)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AA'})
    )
    cvv = forms.CharField(
        max_length=3,
        required=False,
        label="CVV",
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password', 'maxlength': '3'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        mode_paiement = cleaned_data.get('mode_paiement')
        
        if mode_paiement == 'carte':
            if not cleaned_data.get('numero_carte'):
                raise forms.ValidationError("Le numéro de carte est requis pour le paiement par carte.")
            if not cleaned_data.get('date_expiration'):
                raise forms.ValidationError("La date d'expiration est requise.")
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError("Le CVV est requis.")
        
        return cleaned_data


class GestionReservationForm(forms.Form):
    """Formulaire public pour retrouver une réservation"""
    code_reservation = forms.CharField(
        label="Code du dossier / N° de commande",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'EX: AB12CD34'
        })
    )
    email = forms.EmailField(
        label="Adresse email utilisée",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@email.com'
        })
    )


class AnnulationReservationForm(forms.Form):
    """Formulaire dédié à l'annulation publique"""
    reservation_id = forms.IntegerField(widget=forms.HiddenInput())
    code_reservation = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.HiddenInput())


class ReprogrammationReservationForm(forms.Form):
    """Formulaire pour changer l'horaire d'une réservation"""
    reservation_id = forms.IntegerField(widget=forms.HiddenInput())
    code_reservation = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.HiddenInput())
    nouvelle_date = forms.DateField(
        label="Nouvelle date de voyage",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': str(date.today())
        })
    )
    nouveau_train = forms.ModelChoiceField(
        label="Choisissez un nouvel horaire",
        queryset=Train.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        if reservation:
            queryset = Train.objects.filter(
                gare_depart=reservation.train.gare_depart,
                gare_arrivee=reservation.train.gare_arrivee,
                actif=True
            ).order_by('heure_depart')
            self.fields['nouveau_train'].queryset = queryset
            self.fields['nouvelle_date'].widget.attrs['min'] = str(date.today())

    def clean_nouvelle_date(self):
        nouvelle_date = self.cleaned_data['nouvelle_date']
        if nouvelle_date < date.today():
            raise forms.ValidationError("La nouvelle date doit être ultérieure ou égale à aujourd'hui.")
        return nouvelle_date


class RetardTrainForm(forms.ModelForm):
    """Formulaire pour signaler un retard"""
    class Meta:
        model = RetardTrain
        fields = ['train', 'date_voyage', 'minutes_retard', 'motif', 'statut']
        widgets = {
            'train': forms.Select(attrs={'class': 'form-select'}),
            'date_voyage': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'minutes_retard': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class MaintenanceTrainForm(forms.ModelForm):
    """Formulaire pour planifier une maintenance"""
    class Meta:
        model = MaintenanceTrain
        fields = ['train', 'type_maintenance', 'description', 'date_debut', 'date_fin', 'statut', 'responsable']
        widgets = {
            'train': forms.Select(attrs={'class': 'form-select'}),
            'type_maintenance': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        date_debut = cleaned.get('date_debut')
        date_fin = cleaned.get('date_fin')
        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        return cleaned
