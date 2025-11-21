from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import ProfilUtilisateur
from reservations.models import CarteReduction, CarteReductionUtilisateur
from datetime import date


class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription"""
    email = forms.EmailField(required=True, label="Adresse e-mail")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    
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
        return user


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
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = CarteReductionUtilisateur
        fields = ['carte', 'numero_carte', 'date_expiration']
        widgets = {
            'numero_carte': forms.TextInput(attrs={'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def clean_date_expiration(self):
        date_expiration = self.cleaned_data.get('date_expiration')
        if date_expiration and date_expiration < date.today():
            raise forms.ValidationError("La date d'expiration ne peut pas être dans le passé.")
        return date_expiration

