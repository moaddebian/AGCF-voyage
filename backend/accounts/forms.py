from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import ProfilUtilisateur
from reservations.models import CarteReduction, CarteReductionUtilisateur
from datetime import date


class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription"""
    email = forms.EmailField(required=True, label="Adresse e-mail")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    carte = forms.ModelChoiceField(
        queryset=CarteReduction.objects.filter(actif=True),
        required=False,
        label="Type de carte de réduction",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    numero_carte = forms.CharField(
        max_length=50,
        required=False,
        label="Numéro de carte",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AGCF-XXXX-XXXX'})
    )
    date_expiration_carte = forms.DateField(
        required=False,
        label="Date d'expiration",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(date.today())})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            HTML('<hr><h5 class="mb-3"><i class="bi bi-credit-card"></i> Carte de réduction (optionnel)</h5>'),
            HTML('<p class="text-muted">Ajoutez votre carte de réduction dès maintenant si vous en possédez une. Vous pourrez aussi l\'ajouter plus tard depuis votre profil.</p>'),
            Row(
                Column('carte', css_class='form-group col-md-6 mb-0'),
                Column('numero_carte', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('date_expiration_carte', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', "S'inscrire", css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            ProfilUtilisateur.objects.create(utilisateur=user)
            carte = self.cleaned_data.get('carte')
            numero = self.cleaned_data.get('numero_carte')
            date_exp = self.cleaned_data.get('date_expiration_carte')
            if carte and numero and date_exp:
                CarteReductionUtilisateur.objects.create(
                    utilisateur=user,
                    carte=carte,
                    numero_carte=numero,
                    date_expiration=date_exp
                )
        return user

    def clean(self):
        cleaned = super().clean()
        carte = cleaned.get('carte')
        numero = cleaned.get('numero_carte')
        date_exp = cleaned.get('date_expiration_carte')
        if carte or numero or date_exp:
            if not carte:
                self.add_error('carte', "Sélectionnez un type de carte.")
            if not numero:
                self.add_error('numero_carte', "Indiquez le numéro de la carte.")
            if not date_exp:
                self.add_error('date_expiration_carte', "Indiquez la date d'expiration.")
            elif date_exp < date.today():
                self.add_error('date_expiration_carte', "La date d'expiration doit être dans le futur.")
        return cleaned


class ModifierProfilForm(forms.ModelForm):
    """Formulaire de modification du profil"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Adresse e-mail")
    
    class Meta:
        model = ProfilUtilisateur
        fields = ['telephone', 'adresse', 'ville', 'code_postal', 'date_naissance']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, user, commit=True):
        profil = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profil.save()
        return profil


class CarteReductionForm(forms.ModelForm):
    """Formulaire pour ajouter une carte de réduction"""
    carte = forms.ModelChoiceField(
        queryset=CarteReduction.objects.filter(actif=True),
        label="Type de carte",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    numero_carte = forms.CharField(
        label="Numéro de carte",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le numéro de votre carte'}),
        required=True
    )
    date_expiration = forms.DateField(
        label="Date d'expiration",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = CarteReductionUtilisateur
        fields = ['carte', 'numero_carte', 'date_expiration']
    
    def clean_date_expiration(self):
        date_expiration = self.cleaned_data.get('date_expiration')
        if date_expiration and date_expiration < date.today():
            raise forms.ValidationError("La date d'expiration ne peut pas être dans le passé.")
        return date_expiration
    
    def clean_numero_carte(self):
        numero_carte = self.cleaned_data.get('numero_carte')
        if not numero_carte or len(numero_carte.strip()) == 0:
            raise forms.ValidationError("Le numéro de carte est requis.")
        return numero_carte.strip()

