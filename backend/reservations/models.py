from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from datetime import date


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
    nombre_voitures = models.IntegerField(default=8, validators=[MinValueValidator(1)], help_text="Nombre de voitures dans le train")
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

    def est_en_maintenance(self, cible_date):
        """Indique si le train est indisponible pour la date donnée"""
        return self.maintenances.filter(
            date_debut__lte=cible_date,
            date_fin__gte=cible_date,
            statut__in=['planifie', 'en_cours']
        ).exists()
    
    def get_gares_intermediaires(self):
        """Retourne toutes les gares du trajet (départ + intermédiaires + arrivée) dans l'ordre"""
        gares = [self.gare_depart]
        gares.extend([arret.gare for arret in self.arrets_intermediaires.all().order_by('ordre')])
        gares.append(self.gare_arrivee)
        return gares
    
    def passe_par_gare(self, gare):
        """Vérifie si le train passe par une gare donnée"""
        if gare == self.gare_depart or gare == self.gare_arrivee:
            return True
        return self.arrets_intermediaires.filter(gare=gare).exists()
    
    def gare_est_entre_depart_et_arrivee(self, gare, gare_depart_recherche, gare_arrivee_recherche):
        """Vérifie si une gare est entre le départ et l'arrivée recherchés"""
        gares_trajet = self.get_gares_intermediaires()
        
        # Trouver les indices des gares de recherche
        try:
            idx_depart = next(i for i, g in enumerate(gares_trajet) if g == gare_depart_recherche)
            idx_arrivee = next(i for i, g in enumerate(gares_trajet) if g == gare_arrivee_recherche)
            idx_gare = next(i for i, g in enumerate(gares_trajet) if g == gare)
            
            # Vérifier que la gare est entre le départ et l'arrivée
            return idx_depart < idx_gare < idx_arrivee
        except (StopIteration, ValueError):
            return False


class ArretIntermediaire(models.Model):
    """Modèle pour représenter un arrêt intermédiaire d'un train"""
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='arrets_intermediaires')
    gare = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='arrets_intermediaires')
    ordre = models.PositiveIntegerField(help_text="Ordre de passage dans le trajet (1 = première gare après le départ)")
    heure_passage = models.TimeField(help_text="Heure de passage à cette gare", null=True, blank=True)
    
    class Meta:
        ordering = ['train', 'ordre']
        verbose_name = "Arrêt intermédiaire"
        verbose_name_plural = "Arrêts intermédiaires"
        unique_together = ['train', 'ordre']
    
    def __str__(self):
        return f"{self.train.numero} - {self.gare.nom} (ordre {self.ordre})"


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
    
    def nombre_utilisations_aujourdhui(self):
        """Retourne le nombre de fois que cette carte a été utilisée aujourd'hui"""
        aujourdhui = date.today()
        return Reservation.objects.filter(
            carte_reduction=self,
            date_reservation__date=aujourdhui,
            statut__in=['en_attente', 'confirmee', 'utilisee']
        ).count()
    
    def peut_utiliser_aujourdhui(self):
        """Vérifie si la carte peut être utilisée aujourd'hui (max 2 fois par jour)"""
        return self.nombre_utilisations_aujourdhui() < 2
    
    def est_valide(self):
        """Vérifie si la carte est valide (non expirée)"""
        return self.date_expiration >= date.today()


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
        today = timezone.now().date()
        return self.actif and self.date_debut <= today <= self.date_fin


class RetardTrain(models.Model):
    """Suivi des retards déclarés pour les trains"""
    STATUT_CHOICES = [
        ('signale', 'Signalé'),
        ('en_cours', 'En cours de résolution'),
        ('resolu', 'Résolu'),
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='retards')
    date_voyage = models.DateField()
    minutes_retard = models.PositiveIntegerField()
    motif = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='signale')
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_voyage', '-cree_le']
        verbose_name = "Retard"
        verbose_name_plural = "Retards"
        unique_together = ['train', 'date_voyage']

    def __str__(self):
        return f"Retard {self.train.numero} ({self.date_voyage})"


class MaintenanceTrain(models.Model):
    """Planification de la maintenance des trains"""
    STATUT_CHOICES = [
        ('planifie', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='maintenances')
    type_maintenance = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    responsable = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenances"

    def __str__(self):
        return f"Maintenance {self.train.numero} ({self.type_maintenance})"

    def est_active(self, cible_date=None):
        cible = cible_date or timezone.now().date()
        return self.date_debut <= cible <= self.date_fin and self.statut in ['planifie', 'en_cours']
