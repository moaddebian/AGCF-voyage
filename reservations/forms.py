from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Gare, Train, CarteReductionUtilisateur, Reservation, Passager, OffrePromotion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from datetime import date, datetime


class RechercheTrainForm(forms.Form):
    """Formulaire de recherche de trains"""
    gare_depart = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare de départ",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gare_arrivee = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare d'arrivée",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_depart = forms.DateField(
        label="Date de départ",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(date.today())})
    )
    heure_depart = forms.TimeField(
        label="Heure de départ (optionnel)",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        gare_depart = cleaned_data.get('gare_depart')
        gare_arrivee = cleaned_data.get('gare_arrivee')
        date_depart = cleaned_data.get('date_depart')
        
        if gare_depart and gare_arrivee:
            if gare_depart == gare_arrivee:
                raise forms.ValidationError("La gare de départ et d'arrivée doivent être différentes.")
        
        if date_depart and date_depart < date.today():
            raise forms.ValidationError("La date de départ ne peut pas être dans le passé.")
        
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
            self.fields['carte_reduction'].queryset = CarteReductionUtilisateur.objects.filter(
                utilisateur=user,
                date_expiration__gte=date.today()
            )


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

