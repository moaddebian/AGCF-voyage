from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Gare(models.Model):
    """Modèle pour représenter une gare"""
    nom = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    adresse = models.TextField()
    
    class Meta:
        ordering = ['ville', 'nom']
        verbose_name = "Gare"
        verbose_name_plural = "Gares"
    
    def __str__(self):
        return f"{self.nom} ({self.ville})"


class Train(models.Model):
    """Modèle pour représenter un train"""
    CLASSE_CHOICES = [
        ('1', 'Première classe'),
        ('2', 'Deuxième classe'),
    ]
    
    numero = models.CharField(max_length=20, unique=True)
    gare_depart = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='trains_depart')
    gare_arrivee = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='trains_arrivee')
    heure_depart = models.TimeField()
    heure_arrivee = models.TimeField()
    duree = models.DurationField()
    classe = models.CharField(max_length=1, choices=CLASSE_CHOICES, default='2')
    prix_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    places_disponibles = models.IntegerField(validators=[MinValueValidator(0)])
    actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['heure_depart']
        verbose_name = "Train"
        verbose_name_plural = "Trains"
    
    def __str__(self):
        return f"Train {self.numero} : {self.gare_depart.ville} → {self.gare_arrivee.ville}"
    
    @property
    def duree_formatee(self):
        """Retourne la durée formatée en heures et minutes"""
        total_seconds = int(self.duree.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h{minutes:02d}"


class CarteReduction(models.Model):
    """Modèle pour les cartes de réduction"""
    TYPE_CHOICES = [
        ('jeune', 'Carte Jeune'),
        ('senior', 'Carte Senior'),
        ('famille', 'Carte Famille'),
        ('weekend', 'Carte Weekend'),
    ]
    
    type_carte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100)
    reduction_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Carte de réduction"
        verbose_name_plural = "Cartes de réduction"
    
    def __str__(self):
        return f"{self.nom} (-{self.reduction_pourcentage}%)"


class CarteReductionUtilisateur(models.Model):
    """Carte de réduction associée à un utilisateur"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cartes_reduction')
    carte = models.ForeignKey(CarteReduction, on_delete=models.CASCADE)
    numero_carte = models.CharField(max_length=50)
    date_expiration = models.DateField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Carte de réduction utilisateur"
        verbose_name_plural = "Cartes de réduction utilisateurs"
        unique_together = ['utilisateur', 'numero_carte']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.carte.nom}"


class Reservation(models.Model):
    """Modèle pour représenter une réservation"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('utilisee', 'Utilisée'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('cheque', 'Chèque'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='reservations')
    date_voyage = models.DateField()
    nombre_places = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    carte_reduction = models.ForeignKey(CarteReductionUtilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    reduction_appliquee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, null=True, blank=True)
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    code_reservation = models.CharField(max_length=20, unique=True)
    
    class Meta:
        ordering = ['-date_reservation']
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
    
    def __str__(self):
        return f"Réservation {self.code_reservation} - {self.utilisateur.username}"
    
    def calculer_prix_total(self):
        """Calcule le prix total avec réduction"""
        prix_base = self.prix_unitaire * self.nombre_places
        if self.carte_reduction:
            reduction = prix_base * (self.carte_reduction.carte.reduction_pourcentage / 100)
            self.reduction_appliquee = reduction
            return prix_base - reduction
        return prix_base


class Passager(models.Model):
    """Informations des passagers pour une réservation"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='passagers')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    
    class Meta:
        verbose_name = "Passager"
        verbose_name_plural = "Passagers"
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class OffrePromotion(models.Model):
    """Modèle pour les offres et promotions"""
    titre = models.CharField(max_length=200)
    description = models.TextField()
    reduction_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    date_debut = models.DateField()
    date_fin = models.DateField()
    actif = models.BooleanField(default=True)
    image = models.ImageField(upload_to='offres/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Offre promotion"
        verbose_name_plural = "Offres promotions"
    
    def __str__(self):
        return self.titre
    
    def est_valide(self):
        """Vérifie si l'offre est actuellement valide"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.actif and self.date_debut <= today <= self.date_fin

