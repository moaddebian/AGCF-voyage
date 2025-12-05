# 🎓 GUIDE DE FORMATION - AGCF VOYAGES
## Visite guidée du code pour nouveaux développeurs

---

## 📋 TABLE DES MATIÈRES

1. [Introduction](#introduction)
2. [Architecture générale](#architecture-générale)
3. [PARTIE 1 : BACKEND - Structure des données](#partie-1--backend)
4. [PARTIE 2 : FRONTEND - Interactions utilisateur](#partie-2--frontend)
5. [Flux de données complet](#flux-de-données-complet)
6. [Bonnes pratiques et patterns](#bonnes-pratiques)

---

## 🎯 INTRODUCTION

### Qu'est-ce que ce projet ?
**AGCF Voyages** est une application web Django complète permettant de :
- Rechercher des trains entre deux gares
- Réserver des billets avec gestion des passagers
- Appliquer des cartes de réduction
- Gérer les réservations (annulation, modification)
- Générer des billets PDF avec QR codes
- Analyser les revenus et le volume de passagers (admin)

### Technologies utilisées
- **Backend** : Django 5.2.8 (Python 3.14.0)
- **Base de données** : MySQL
- **Frontend** : Bootstrap 5, Chart.js, JavaScript vanilla
- **Génération PDF** : ReportLab
- **QR Codes** : qrcode library

---

## 🏗️ ARCHITECTURE GÉNÉRALE

```
AGCF/
├── backend/              # Application Django (logique métier)
│   ├── accounts/         # Gestion des utilisateurs
│   ├── reservations/     # Application principale (réservations)
│   └── agcf_voyage/     # Configuration Django
├── frontend/            # Interface utilisateur
│   ├── templates/       # Templates HTML
│   ├── static/         # CSS, JavaScript, images
│   └── media/          # Fichiers uploadés (billets PDF)
└── venv/               # Environnement virtuel Python
```

**Principe de séparation** :
- **Backend** : Toute la logique métier, les modèles, les vues
- **Frontend** : Présentation, templates, styles, interactions

---

## 📦 PARTIE 1 : BACKEND - Structure des données

### 🎯 Objectif de cette partie
Comprendre **comment les données sont structurées** et **comment elles sont exposées** via l'API Django.

---

### 📁 ÉTAPE 1 : Configuration du projet (`agcf_voyage/`)

#### 📄 `settings.py` - Le cerveau de Django

**Rôle** : Configure TOUT le comportement de Django.

**Pourquoi ce fichier existe** :
Django a besoin de savoir :
- Quelle base de données utiliser
- Où trouver les templates
- Quelles applications sont installées
- Comment gérer les fichiers statiques
- Les paramètres de sécurité

**Exemple concret** :

```python
# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'agcf_voyage',
        'USER': 'root',
        'PASSWORD': 'Mouad1232002',
        # ...
    }
}
```

**Pourquoi MySQL et pas SQLite ?**
- SQLite est parfait pour le développement
- MySQL est nécessaire pour la production (performances, concurrence)
- Le code utilise `dj-database-url` pour supporter les deux

**Configuration des templates** :

```python
TEMPLATES = [{
    'DIRS': [FRONTEND_DIR / 'templates'],  # Où chercher les templates
    'APP_DIRS': True,  # Chercher aussi dans chaque app
}]
```

**Pourquoi cette structure ?**
- `FRONTEND_DIR / 'templates'` : Templates globaux (base.html)
- `APP_DIRS = True` : Templates spécifiques à chaque app (accounts/, reservations/)

**Applications installées** :

```python
INSTALLED_APPS = [
    'django.contrib.admin',    # Interface d'administration
    'django.contrib.auth',     # Authentification
    'reservations',            # Notre app principale
    'accounts',                # Notre app utilisateurs
    'crispy_forms',            # Formulaires stylisés
]
```

**Pourquoi cette organisation ?**
- Django fonctionne par "applications" (apps)
- Chaque app est indépendante et réutilisable
- `reservations` et `accounts` sont nos apps métier

---

#### 📄 `urls.py` - Le routeur principal

**Rôle** : Définit toutes les URLs du site et les associe aux vues.

**Pourquoi ce fichier existe** :
Quand un utilisateur visite `/accounts/profil/`, Django doit savoir quelle fonction Python appeler.

**Exemple concret** :

```python
urlpatterns = [
    path('admin/analytics/', ...),      # Analyse admin
    path('admin/', admin.site.urls),    # Interface admin Django
    path('', include('reservations.urls')),      # Routes de réservation
    path('accounts/', include('accounts.urls')), # Routes utilisateurs
]
```

**Comment ça marche ?**
1. Utilisateur visite `/accounts/profil/`
2. Django cherche dans `urlpatterns`
3. Trouve `path('accounts/', include('accounts.urls'))`
4. Passe à `accounts/urls.py` qui cherche `profil/`
5. Appelle la fonction `profil(request)`

**Pourquoi `include()` ?**
- Permet de séparer les URLs par application
- `accounts/urls.py` gère toutes les URLs `/accounts/*`
- Plus maintenable et organisé

---

### 📁 ÉTAPE 2 : Modèles de données (`reservations/models.py`)

**Rôle** : Définit la structure de la base de données en Python.

**Pourquoi des modèles Django ?**
- Au lieu d'écrire du SQL, on écrit du Python
- Django génère automatiquement les tables
- Protection contre les injections SQL
- Relations entre tables gérées automatiquement

---

#### 🗄️ Modèle 1 : `Gare`

```python
class Gare(models.Model):
    nom = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    adresse = models.TextField()
```

**Explication ligne par ligne** :
- `models.Model` : Hérite de la classe de base Django
- `CharField` : Champ texte de longueur limitée
- `unique=True` : Le code doit être unique (ex: "PAR" pour Paris)
- `TextField` : Champ texte illimité (pour l'adresse complète)

**Pourquoi ce modèle ?**
- Chaque train a une gare de départ et d'arrivée
- Les gares sont réutilisables (plusieurs trains partent de la même gare)
- Le code unique permet une identification rapide

**En base de données, ça devient** :
```sql
CREATE TABLE reservations_gare (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(200),
    ville VARCHAR(100),
    code VARCHAR(10) UNIQUE,
    adresse TEXT
);
```

---

#### 🗄️ Modèle 2 : `Train`

```python
class Train(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    gare_depart = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='trains_depart')
    gare_arrivee = models.ForeignKey(Gare, on_delete=models.CASCADE, related_name='trains_arrivee')
    heure_depart = models.TimeField()
    heure_arrivee = models.TimeField()
    duree = models.DurationField()
    prix_base = models.DecimalField(max_digits=10, decimal_places=2)
    places_disponibles = models.IntegerField(validators=[MinValueValidator(0)])
```

**Concepts importants** :

**1. `ForeignKey`** :
```python
gare_depart = models.ForeignKey(Gare, ...)
```
- Crée une relation "plusieurs trains → une gare"
- En SQL : `gare_depart_id INT REFERENCES gare(id)`
- Permet d'accéder : `train.gare_depart.nom`

**Pourquoi `related_name='trains_depart'` ?**
- Permet d'accéder depuis une gare : `gare.trains_depart.all()`
- Liste tous les trains partant de cette gare

**2. `on_delete=models.CASCADE`** :
- Si une gare est supprimée, tous les trains associés sont supprimés
- Évite les données orphelines

**3. `DecimalField` pour les prix** :
```python
prix_base = models.DecimalField(max_digits=10, decimal_places=2)
```
- **Pourquoi pas `FloatField` ?**
  - Les floats ont des erreurs de précision (0.1 + 0.2 = 0.30000000000000004)
  - Pour l'argent, on a besoin de précision exacte
  - `Decimal` garantit la précision

**4. Méthodes personnalisées** :

```python
def est_en_maintenance(self, cible_date):
    """Indique si le train est indisponible pour la date donnée"""
    return self.maintenances.filter(
        date_debut__lte=cible_date,
        date_fin__gte=cible_date,
        statut__in=['planifie', 'en_cours']
    ).exists()
```

**Pourquoi cette méthode ?**
- Logique métier réutilisable
- Au lieu de répéter le code partout, on appelle `train.est_en_maintenance(date)`
- Plus lisible et maintenable

---

#### 🗄️ Modèle 3 : `Reservation` (LE PLUS IMPORTANT)

```python
class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('utilisee', 'Utilisée'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    date_voyage = models.DateField()
    nombre_places = models.IntegerField(validators=[MinValueValidator(1)])
    carte_reduction = models.ForeignKey(CarteReductionUtilisateur, null=True, blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    reduction_appliquee = models.DecimalField(max_digits=10, decimal_places=2)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    code_reservation = models.CharField(max_length=20, unique=True)
```

**Concepts avancés** :

**1. `STATUT_CHOICES`** :
```python
STATUT_CHOICES = [('en_attente', 'En attente de paiement'), ...]
statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
```
- Limite les valeurs possibles
- Dans l'admin Django, affiche un dropdown
- Validation automatique

**Pourquoi pas un enum Python ?**
- Django peut stocker directement la valeur en DB
- Plus simple pour les migrations
- Compatible avec les anciennes versions

**2. `null=True, blank=True`** :
```python
carte_reduction = models.ForeignKey(..., null=True, blank=True)
```
- `null=True` : La colonne DB peut être NULL
- `blank=True` : Le formulaire peut être vide
- **Pourquoi ?** : La carte de réduction est optionnelle

**3. Méthode de calcul** :

```python
def calculer_prix_total(self):
    """Calcule le prix total avec réduction"""
    prix_base = self.prix_unitaire * self.nombre_places
    if self.carte_reduction:
        reduction = prix_base * (self.carte_reduction.carte.reduction_pourcentage / 100)
        self.reduction_appliquee = reduction
        return prix_base - reduction
    return prix_base
```

**Pourquoi cette méthode dans le modèle ?**
- Logique métier centralisée
- Réutilisable partout : `reservation.calculer_prix_total()`
- Facile à tester
- Si la règle change, on modifie un seul endroit

**Exemple d'utilisation** :
```python
reservation = Reservation.objects.get(code_reservation='ABC123')
prix_final = reservation.calculer_prix_total()
# Si 2 places à 50€ avec carte -30% : (2 * 50) - 30 = 70€
```

---

#### 🗄️ Modèle 4 : `ArretIntermediaire`

```python
class ArretIntermediaire(models.Model):
    train = models.ForeignKey(Train, related_name='arrets_intermediaires')
    gare = models.ForeignKey(Gare)
    ordre = models.PositiveIntegerField()
    heure_passage = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['train', 'ordre']
```

**Pourquoi ce modèle ?**
- Un train peut passer par plusieurs gares
- Exemple : Paris → Lyon → Marseille
- `ordre=1` = Lyon, `ordre=2` = Marseille

**`unique_together`** :
- Empêche d'avoir deux arrêts avec le même ordre pour un train
- Garantit l'unicité : un train ne peut pas avoir deux arrêts à l'ordre 1

**Utilisation** :
```python
train = Train.objects.get(numero='TGV123')
gares = train.get_gares_intermediaires()
# Retourne : [Gare Paris, Gare Lyon, Gare Marseille]
```

---

### 📁 ÉTAPE 3 : Formulaires (`reservations/forms.py`)

**Rôle** : Valide et structure les données entrées par l'utilisateur.

**Pourquoi des formulaires Django ?**
- Validation automatique
- Protection CSRF intégrée
- Génération HTML automatique
- Gestion des erreurs

---

#### 📝 Formulaire : `RechercheTrainForm`

```python
class RechercheTrainForm(forms.Form):
    gare_depart = forms.ModelChoiceField(
        queryset=Gare.objects.all(),
        label="Gare de départ",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_depart = forms.DateField(
        label="Date de départ",
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    nombre_voyageurs = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1
    )
```

**Explication** :

**1. `ModelChoiceField`** :
- Crée automatiquement un `<select>` avec toutes les gares
- Validation : vérifie que la gare existe
- Plus simple que de créer le select manuellement

**2. `initial=date.today`** :
- Valeur par défaut = aujourd'hui
- Améliore l'UX (l'utilisateur n'a pas à sélectionner la date)

**3. `min_value=1, max_value=10`** :
- Validation automatique
- Si l'utilisateur entre 0 ou 11, le formulaire est invalide

**Utilisation dans une vue** :

```python
def home(request):
    if request.method == 'POST':
        form = RechercheTrainForm(request.POST)
        if form.is_valid():
            # Les données sont validées et nettoyées
            gare_depart = form.cleaned_data['gare_depart']
            date_depart = form.cleaned_data['date_depart']
            # On peut maintenant utiliser ces données en toute sécurité
```

**Pourquoi `cleaned_data` ?**
- Django nettoie et valide les données
- Protection contre les injections
- Conversion automatique (string → date, etc.)

---

### 📁 ÉTAPE 4 : Vues (`reservations/views.py`)

**Rôle** : Traite les requêtes HTTP et retourne des réponses.

**Architecture Django (MVT)** :
- **Model** : Structure des données (models.py)
- **View** : Logique métier (views.py)
- **Template** : Présentation (templates/)

---

#### 🔍 Vue : `home()` - Page d'accueil

```python
def home(request):
    """Page d'accueil avec formulaire de recherche"""
    form = RechercheTrainForm()
    
    # Récupérer les offres promotionnelles actives
    today = timezone.now().date()
    offres = OffrePromotion.objects.filter(
        actif=True,
        date_debut__lte=today,
        date_fin__gte=today
    )[:3]  # Limiter à 3 offres
    
    if request.method == 'POST':
        form = RechercheTrainForm(request.POST)
        if form.is_valid():
            # Rediriger vers la page de résultats
            return redirect('reservations:recherche_resultats', ...)
    
    context = {
        'form': form,
        'offres': offres,
    }
    return render(request, 'reservations/home.html', context)
```

**Explication ligne par ligne** :

**1. `def home(request)`** :
- `request` : Objet contenant toutes les infos de la requête HTTP
- Méthode GET ou POST, données du formulaire, cookies, session, etc.

**2. `form = RechercheTrainForm()`** :
- Crée un formulaire vide (pour GET)
- Sera affiché dans le template

**3. Requête QuerySet** :
```python
offres = OffrePromotion.objects.filter(
    actif=True,
    date_debut__lte=today,
    date_fin__gte=today
)[:3]
```
- `objects.filter()` : Filtre les objets en base
- `date_debut__lte=today` : Date début <= aujourd'hui
- `[:3]` : Limite à 3 résultats (optimisation)

**Pourquoi `[:3]` et pas `.filter()` ?**
- Plus performant : Django limite en SQL
- Évite de charger toutes les offres en mémoire

**4. `if request.method == 'POST'`** :
- Si l'utilisateur a soumis le formulaire
- Traite les données

**5. `form.is_valid()`** :
- Valide le formulaire
- Si valide : `form.cleaned_data` contient les données
- Si invalide : `form.errors` contient les erreurs

**6. `redirect()`** :
- Redirige vers une autre page
- Évite le double POST (si l'utilisateur actualise, pas de nouvelle soumission)

**7. `context`** :
- Dictionnaire de données à passer au template
- Accessible dans le template : `{{ form }}`, `{{ offres }}`

**8. `render()`** :
- Combine le template HTML avec le context
- Retourne une réponse HTTP complète

---

#### 🔍 Vue : `recherche_resultats()` - Résultats de recherche

```python
def recherche_resultats(request, gare_depart_id, gare_arrivee_id, date_depart, gare_intermediaire_id='0'):
    # Récupérer les gares
    gare_depart = get_object_or_404(Gare, id=gare_depart_id)
    gare_arrivee = get_object_or_404(Gare, id=gare_arrivee_id)
    
    # Convertir la date
    date_depart = datetime.strptime(date_depart, '%Y-%m-%d').date()
    
    # Requête de base : trains actifs
    trains = Train.objects.filter(actif=True)
    
    # Filtrer par gares
    trains = trains.filter(
        Q(gare_depart=gare_depart) | Q(arrets_intermediaires__gare=gare_depart),
        Q(gare_arrivee=gare_arrivee) | Q(arrets_intermediaires__gare=gare_arrivee)
    )
    
    # Exclure les trains en maintenance
    trains = trains.exclude(
        maintenances__date_debut__lte=date_depart,
        maintenances__date_fin__gte=date_depart,
        maintenances__statut__in=['planifie', 'en_cours']
    )
    
    # Filtrer par places disponibles
    trains = trains.filter(places_disponibles__gte=nombre_voyageurs)
    
    return render(request, 'reservations/recherche_resultats.html', {
        'trains': trains,
        'gare_depart': gare_depart,
        'gare_arrivee': gare_arrivee,
    })
```

**Concepts avancés** :

**1. `get_object_or_404()`** :
```python
gare_depart = get_object_or_404(Gare, id=gare_depart_id)
```
- Si la gare existe : retourne l'objet
- Si elle n'existe pas : retourne une erreur 404 (page non trouvée)
- **Pourquoi ?** : Meilleure UX que de planter avec une erreur

**2. Requêtes complexes avec `Q`** :
```python
trains = trains.filter(
    Q(gare_depart=gare_depart) | Q(arrets_intermediaires__gare=gare_depart)
)
```
- `Q()` : Permet des requêtes complexes (OR, AND, NOT)
- `|` : OR (le train part de cette gare OU passe par cette gare)
- `arrets_intermediaires__gare` : Accès aux relations (lookup Django)

**Pourquoi cette complexité ?**
- Un train peut partir directement d'une gare
- OU passer par cette gare en arrêt intermédiaire
- Il faut gérer les deux cas

**3. Exclusion avec `exclude()`** :
```python
trains = trains.exclude(maintenances__date_debut__lte=date_depart, ...)
```
- Exclut les trains en maintenance à cette date
- **Pourquoi `exclude()` et pas `filter()` ?**
  - `filter()` : Inclut seulement
  - `exclude()` : Exclut (plus lisible pour "ne pas en maintenance")

---

#### 🔍 Vue : `paiement()` - Traitement du paiement

```python
@login_required
def paiement(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        
        if not cart:
            messages.error(request, "Votre panier est vide.")
            return redirect('reservations:panier')
        
        # Créer les réservations
        reservations_crees = []
        for item in cart:
            train = Train.objects.get(id=item['train_id'])
            
            # Générer un code unique
            code_reservation = secrets.token_urlsafe(8).upper()[:8]
            
            # Calculer le prix
            prix_unitaire = train.prix_base
            if item.get('carte_reduction_id'):
                carte = CarteReductionUtilisateur.objects.get(id=item['carte_reduction_id'])
                reduction = prix_unitaire * (carte.carte.reduction_pourcentage / 100)
            else:
                reduction = Decimal('0.00')
            
            prix_total = (prix_unitaire * item['nombre_places']) - reduction
            
            # Créer la réservation
            reservation = Reservation.objects.create(
                utilisateur=request.user,
                train=train,
                date_voyage=item['date_voyage'],
                nombre_places=item['nombre_places'],
                prix_unitaire=prix_unitaire,
                reduction_appliquee=reduction,
                prix_total=prix_total,
                code_reservation=code_reservation,
                statut='confirmee'
            )
            
            # Créer les passagers
            for passager_data in item['passagers']:
                Passager.objects.create(
                    reservation=reservation,
                    nom=passager_data['nom'],
                    prenom=passager_data['prenom'],
                    date_naissance=passager_data['date_naissance']
                )
            
            # Générer le billet PDF
            generer_billet_pdf(reservation)
            
            reservations_crees.append(reservation)
        
        # Vider le panier
        request.session['cart'] = []
        
        # Rediriger vers la confirmation
        return redirect('reservations:confirmation', code=reservations_crees[0].code_reservation)
```

**Concepts importants** :

**1. `@login_required`** :
- Décorateur Django
- Si l'utilisateur n'est pas connecté → redirection vers la page de connexion
- **Pourquoi ?** : Le paiement nécessite une authentification

**2. Session Django** :
```python
cart = request.session.get('cart', [])
```
- Stocke des données temporaires côté serveur
- Persiste entre les requêtes (via cookies)
- **Pourquoi une session ?**
  - Le panier doit persister même si l'utilisateur ferme le navigateur
  - Plus sécurisé que de stocker dans les cookies (données sensibles)

**3. Génération de code unique** :
```python
code_reservation = secrets.token_urlsafe(8).upper()[:8]
```
- `secrets` : Module Python sécurisé (aléatoire cryptographique)
- `token_urlsafe(8)` : Génère une chaîne aléatoire de 8 caractères
- `.upper()[:8]` : Met en majuscules et limite à 8 caractères
- **Pourquoi ?** : Code unique, non devinable, pour identifier la réservation

**4. Transaction atomique** :
```python
reservation = Reservation.objects.create(...)
Passager.objects.create(reservation=reservation, ...)
```
- Si une erreur survient, Django peut rollback
- Garantit la cohérence des données

**5. Génération PDF** :
```python
generer_billet_pdf(reservation)
```
- Fonction utilitaire (dans `utils.py`)
- Génère un PDF avec QR code
- Stocké dans `media/billets/`

---

### 📁 ÉTAPE 5 : Utilitaires (`reservations/utils.py`)

**Rôle** : Fonctions réutilisables pour des tâches spécifiques.

---

#### 🔧 Fonction : `generer_billet_pdf()`

```python
def generer_billet_pdf(reservation):
    """Génère un PDF de billet avec QR code"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import qrcode
    
    # Créer le fichier PDF
    filename = f"billet_{reservation.code_reservation}.pdf"
    filepath = settings.MEDIA_ROOT / 'billets' / filename
    
    # Générer le QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(reservation.code_reservation)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Créer le PDF avec ReportLab
    c = canvas.Canvas(str(filepath), pagesize=letter)
    # ... dessiner le contenu ...
    c.save()
    
    return filepath
```

**Pourquoi cette fonction séparée ?**
- Réutilisable : peut être appelée depuis plusieurs endroits
- Testable : peut être testée indépendamment
- Maintenable : si le format change, on modifie un seul endroit

---

### 📁 ÉTAPE 6 : URLs (`reservations/urls.py`)

**Rôle** : Associe les URLs aux vues.

```python
app_name = 'reservations'

urlpatterns = [
    path('', views.home, name='home'),
    path('recherche/<int:gare_depart_id>/<int:gare_arrivee_id>/<str:date_depart>/', 
         views.recherche_resultats, name='recherche_resultats'),
    path('reserver/<int:train_id>/', views.reserver_train, name='reserver_train'),
    path('paiement/', views.paiement, name='paiement'),
]
```

**Concepts** :

**1. `app_name`** :
- Namespace pour éviter les conflits
- Utilisation : `{% url 'reservations:home' %}`
- Si deux apps ont une vue `home`, pas de conflit

**2. Paramètres d'URL** :
```python
path('recherche/<int:gare_depart_id>/...', views.recherche_resultats, ...)
```
- `<int:gare_depart_id>` : Capture un entier dans l'URL
- Passé comme argument à la vue : `recherche_resultats(request, gare_depart_id=123, ...)`

**3. `name`** :
- Nom unique pour référencer l'URL
- Dans les templates : `{% url 'reservations:home' %}`
- Dans le code Python : `reverse('reservations:home')`

---

## 🎨 PARTIE 2 : FRONTEND - Interactions utilisateur

### 🎯 Objectif de cette partie
Comprendre **comment l'utilisateur interagit** avec les données et **comment elles sont affichées**.

---

### 📁 ÉTAPE 1 : Template de base (`templates/base.html`)

**Rôle** : Template principal hérité par tous les autres.

**Pourquoi un template de base ?**
- Évite la duplication de code (navbar, footer, scripts)
- Changement global en un seul endroit
- Cohérence visuelle

---

#### Structure du template

```django
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}AGCF Voyages{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <a href="{% url 'reservations:home' %}">Accueil</a>
        {% if user.is_authenticated %}
            <a href="{% url 'accounts:profil' %}">Profil</a>
        {% endif %}
    </nav>
    
    <!-- Messages Django -->
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
    
    <!-- Contenu spécifique à chaque page -->
    {% block content %}{% endblock %}
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Concepts Django Template** :

**1. `{% load static %}`** :
- Charge les fichiers statiques (CSS, JS, images)
- Permet d'utiliser `{% static 'images/logo.jpg' %}`

**2. `{% block title %}`** :
- Bloc modifiable par les templates enfants
- Dans `home.html` : `{% block title %}Accueil{% endblock %}`

**3. `{% url 'reservations:home' %}`** :
- Génère l'URL depuis le nom
- Si l'URL change dans `urls.py`, le template s'adapte automatiquement

**4. `{% if user.is_authenticated %}`** :
- Vérifie si l'utilisateur est connecté
- Affiche conditionnellement des éléments

**5. `{% block content %}`** :
- Les templates enfants remplissent ce bloc
- Exemple dans `home.html` :

```django
{% extends 'base.html' %}
{% block content %}
    <h1>Bienvenue</h1>
    <!-- Contenu spécifique à la page d'accueil -->
{% endblock %}
```

---

### 📁 ÉTAPE 2 : Template de recherche (`templates/reservations/home.html`)

**Rôle** : Affiche le formulaire de recherche et les offres.

---

#### Formulaire de recherche

```django
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<form method="post">
    {% csrf_token %}
    
    <div class="row">
        <div class="col-md-6">
            <label>Gare de départ</label>
            {{ form.gare_depart }}
        </div>
        <div class="col-md-6">
            <label>Gare d'arrivée</label>
            {{ form.gare_arrivee }}
        </div>
        <div class="col-md-6">
            <label>Date de départ</label>
            {{ form.date_depart }}
        </div>
    </div>
    
    <button type="submit">Rechercher</button>
</form>
{% endblock %}
```

**Explication** :

**1. `{% extends 'base.html' %}`** :
- Hérite de `base.html`
- Réutilise navbar, footer, styles

**2. `{% csrf_token %}`** :
- Protection CSRF (Cross-Site Request Forgery)
- Django génère un token unique
- **Pourquoi ?** : Empêche les attaques où un site malveillant soumet un formulaire à votre place

**3. `{{ form.gare_depart }}`** :
- Affiche le champ du formulaire Django
- Génère automatiquement le HTML : `<select>...</select>`
- Inclut la validation et les erreurs

**4. `method="post"`** :
- Envoie les données au serveur
- GET = récupérer des données (recherche Google)
- POST = envoyer des données (formulaire)

---

#### Affichage des offres

```django
{% if offres %}
    <div class="row">
        {% for offre in offres %}
            <div class="col-md-4">
                <div class="card">
                    <h5>{{ offre.titre }}</h5>
                    <p>{{ offre.description|truncatewords:20 }}</p>
                    <span class="badge">-{{ offre.reduction_pourcentage }}%</span>
                </div>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

**Concepts** :

**1. `{% if offres %}`** :
- Condition : affiche seulement si `offres` existe et n'est pas vide
- Évite d'afficher une section vide

**2. `{% for offre in offres %}`** :
- Boucle sur la liste `offres` (passée depuis la vue)
- Pour chaque offre, affiche une card

**3. `{{ offre.titre }}`** :
- Affiche l'attribut `titre` de l'objet `offre`
- Échappement automatique (protection XSS)

**4. `|truncatewords:20`** :
- Filtre Django : limite à 20 mots
- Ajoute "..." si plus long
- **Pourquoi ?** : Évite les descriptions trop longues

---

### 📁 ÉTAPE 3 : Template de résultats (`templates/reservations/recherche_resultats.html`)

**Rôle** : Affiche la liste des trains disponibles.

```django
{% for train in trains %}
    <div class="card train-card">
        <div class="card-body">
            <h5>Train {{ train.numero }}</h5>
            <p>
                <i class="bi bi-geo-alt"></i>
                {{ train.gare_depart.ville }} → {{ train.gare_arrivee.ville }}
            </p>
            <p>
                <i class="bi bi-clock"></i>
                Départ : {{ train.heure_depart|time:"H:i" }}
                Arrivée : {{ train.heure_arrivee|time:"H:i" }}
            </p>
            <p>
                <i class="bi bi-currency-euro"></i>
                {{ train.prix_base }}€
            </p>
            <p>
                <i class="bi bi-people"></i>
                {{ train.places_disponibles }} places disponibles
            </p>
            
            <a href="{% url 'reservations:reserver_train' train.id %}" 
               class="btn btn-primary">
                Réserver
            </a>
        </div>
    </div>
{% empty %}
    <p>Aucun train trouvé pour cette recherche.</p>
{% endfor %}
```

**Concepts** :

**1. Accès aux relations** :
```django
{{ train.gare_depart.ville }}
```
- `train.gare_depart` : Accède à l'objet `Gare` (relation ForeignKey)
- `.ville` : Accède à l'attribut `ville` de la gare
- Django fait automatiquement le JOIN SQL

**2. Filtres de template** :
```django
{{ train.heure_depart|time:"H:i" }}
```
- `|time:"H:i"` : Formate l'heure en "14:30"
- Filtres Django : transformation des données pour l'affichage

**3. `{% empty %}`** :
- Affiche un message si la liste est vide
- Meilleure UX que d'afficher rien

**4. URL avec paramètre** :
```django
{% url 'reservations:reserver_train' train.id %}
```
- Passe `train.id` comme paramètre
- Génère : `/reserver/123/` (si train.id = 123)

---

### 📁 ÉTAPE 4 : JavaScript interactif (`static/admin/js/ai_floating_button.js`)

**Rôle** : Gère les interactions dynamiques (AJAX, graphiques).

---

#### Exemple : Chargement des données analytics

```javascript
// Quand le bouton AI est cliqué
document.getElementById('ai-floating-btn').addEventListener('click', function() {
    // Ouvrir le modal
    const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
    modal.show();
    
    // Charger les données via AJAX
    fetch('/admin/analytics/data/?period=30&chart_type=daily')
        .then(response => response.json())
        .then(data => {
            // Créer le graphique Chart.js
            const ctx = document.getElementById('revenueChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.revenue_labels,
                    datasets: [{
                        label: 'Revenus',
                        data: data.revenue_data,
                        borderColor: '#ff6600',
                    }]
                }
            });
        });
});
```

**Concepts** :

**1. AJAX avec `fetch()`** :
- Requête HTTP sans recharger la page
- **Pourquoi ?** : Meilleure UX, plus rapide

**2. Promesses (Promises)** :
```javascript
fetch(...)
    .then(response => response.json())
    .then(data => { ... })
```
- Code asynchrone
- `fetch()` retourne une promesse
- `.then()` exécute quand la requête est terminée

**3. Chart.js** :
- Bibliothèque JavaScript pour les graphiques
- Crée des graphiques interactifs à partir de données JSON

**Pourquoi JavaScript séparé ?**
- Réutilisable
- Plus facile à déboguer
- Peut être mis en cache par le navigateur

---

## 🔄 FLUX DE DONNÉES COMPLET

### Exemple : Processus de réservation (de A à Z)

#### Étape 1 : L'utilisateur visite la page d'accueil

```
1. Navigateur → GET / → Django
2. Django appelle views.home(request)
3. Vue récupère les offres : OffrePromotion.objects.filter(...)
4. Vue crée un formulaire vide : RechercheTrainForm()
5. Vue rend le template : render('home.html', {'form': form, 'offres': offres})
6. Django → HTML → Navigateur
7. Navigateur affiche la page avec le formulaire
```

#### Étape 2 : L'utilisateur remplit et soumet le formulaire

```
1. Navigateur → POST / (avec données formulaire) → Django
2. Django appelle views.home(request) avec request.method == 'POST'
3. Vue crée le formulaire avec les données : RechercheTrainForm(request.POST)
4. Vue valide : form.is_valid()
5. Si valide : Vue redirige vers /recherche/123/456/2025-12-02/
6. Django → HTTP 302 Redirect → Navigateur
7. Navigateur suit la redirection → GET /recherche/.../
```

#### Étape 3 : Affichage des résultats

```
1. Navigateur → GET /recherche/123/456/2025-12-02/ → Django
2. Django appelle views.recherche_resultats(request, gare_depart_id=123, ...)
3. Vue récupère les gares : Gare.objects.get(id=123)
4. Vue filtre les trains :
   - Train.objects.filter(actif=True)
   - .filter(gare_depart=..., gare_arrivee=...)
   - .exclude(maintenances__...)
5. Vue rend le template : render('recherche_resultats.html', {'trains': trains})
6. Template boucle sur trains : {% for train in trains %}
7. Django → HTML → Navigateur
8. Navigateur affiche la liste des trains
```

#### Étape 4 : L'utilisateur clique sur "Réserver"

```
1. Navigateur → GET /reserver/789/ → Django
2. Django appelle views.reserver_train(request, train_id=789)
3. Vue récupère le train : Train.objects.get(id=789)
4. Vue calcule le prix avec réduction (si carte disponible)
5. Vue ajoute au panier (session) : request.session['cart'].append(...)
6. Vue redirige vers /ajouter-passagers/
```

#### Étape 5 : Ajout des passagers

```
1. Navigateur → GET /ajouter-passagers/ → Django
2. Vue affiche le formulaire pour chaque passager
3. Utilisateur remplit les informations
4. POST /ajouter-passagers/ → Django
5. Vue valide et stocke dans la session
6. Vue redirige vers /panier/
```

#### Étape 6 : Paiement

```
1. Navigateur → POST /paiement/ → Django
2. Vue récupère le panier : request.session.get('cart')
3. Pour chaque item du panier :
   a. Crée une réservation : Reservation.objects.create(...)
   b. Crée les passagers : Passager.objects.create(...)
   c. Génère le billet PDF : generer_billet_pdf(reservation)
4. Vue vide le panier : request.session['cart'] = []
5. Vue redirige vers /confirmation/ABC123/
```

---

## ✅ BONNES PRATIQUES ET PATTERNS

### 1. Séparation des responsabilités

**❌ MAUVAIS** :
```python
def home(request):
    # Mélange logique métier et présentation
    html = f"<h1>Bienvenue {request.user.username}</h1>"
    return HttpResponse(html)
```

**✅ BON** :
```python
def home(request):
    # Logique métier seulement
    offres = OffrePromotion.objects.filter(actif=True)
    return render(request, 'home.html', {'offres': offres})
```

**Pourquoi ?**
- Plus maintenable
- Réutilisable
- Testable

---

### 2. Validation des données

**❌ MAUVAIS** :
```python
def paiement(request):
    train_id = request.POST['train_id']  # Peut planter si absent
    train = Train.objects.get(id=train_id)  # Peut planter si n'existe pas
```

**✅ BON** :
```python
def paiement(request):
    form = PaiementForm(request.POST)
    if form.is_valid():
        train_id = form.cleaned_data['train_id']  # Validé et nettoyé
        train = get_object_or_404(Train, id=train_id)  # Gère l'erreur 404
```

**Pourquoi ?**
- Protection contre les erreurs
- Validation centralisée
- Meilleure UX (erreurs claires)

---

### 3. Requêtes optimisées

**❌ MAUVAIS** :
```python
trains = Train.objects.all()
for train in trains:
    print(train.gare_depart.nom)  # Requête SQL pour chaque train !
```

**✅ BON** :
```python
trains = Train.objects.select_related('gare_depart', 'gare_arrivee').all()
for train in trains:
    print(train.gare_depart.nom)  # Données déjà chargées !
```

**Pourquoi ?**
- `select_related()` : Fait un JOIN SQL
- Évite le problème N+1 (1 requête principale + N requêtes pour les relations)
- Beaucoup plus rapide

---

### 4. Gestion des erreurs

**❌ MAUVAIS** :
```python
def recherche_resultats(request, gare_id):
    gare = Gare.objects.get(id=gare_id)  # Plantera si n'existe pas
```

**✅ BON** :
```python
def recherche_resultats(request, gare_id):
    gare = get_object_or_404(Gare, id=gare_id)  # Retourne 404 proprement
    # Ou
    try:
        gare = Gare.objects.get(id=gare_id)
    except Gare.DoesNotExist:
        messages.error(request, "Gare introuvable.")
        return redirect('reservations:home')
```

**Pourquoi ?**
- Meilleure UX (page d'erreur propre)
- Pas de crash de l'application
- Messages d'erreur clairs

---

### 5. Code réutilisable

**❌ MAUVAIS** :
```python
# Code dupliqué dans plusieurs vues
prix_base = train.prix_base * nombre_places
if carte_reduction:
    reduction = prix_base * (carte_reduction.carte.reduction_pourcentage / 100)
    prix_total = prix_base - reduction
else:
    prix_total = prix_base
```

**✅ BON** :
```python
# Dans models.py
class Reservation(models.Model):
    def calculer_prix_total(self):
        prix_base = self.prix_unitaire * self.nombre_places
        if self.carte_reduction:
            reduction = prix_base * (self.carte_reduction.carte.reduction_pourcentage / 100)
            return prix_base - reduction
        return prix_base

# Dans les vues
prix_total = reservation.calculer_prix_total()
```

**Pourquoi ?**
- DRY (Don't Repeat Yourself)
- Si la règle change, un seul endroit à modifier
- Plus facile à tester

---

## 🎓 CONCLUSION

### Ce que vous avez appris

1. **Backend** :
   - Comment les données sont structurées (modèles)
   - Comment elles sont validées (formulaires)
   - Comment elles sont traitées (vues)
   - Comment elles sont exposées (URLs)

2. **Frontend** :
   - Comment les données sont affichées (templates)
   - Comment l'utilisateur interagit (formulaires, JavaScript)
   - Comment les requêtes sont faites (AJAX)

3. **Flux complet** :
   - De la requête HTTP à la réponse HTML
   - Gestion des sessions, panier, paiement

### Prochaines étapes

1. **Lire le code** : Parcourez les fichiers dans l'ordre de ce guide
2. **Tester** : Lancez le serveur et testez chaque fonctionnalité
3. **Modifier** : Essayez d'ajouter une petite fonctionnalité
4. **Comprendre** : Utilisez le debugger Python pour voir le flux en temps réel

### Ressources

- **Documentation Django** : https://docs.djangoproject.com/
- **Bootstrap 5** : https://getbootstrap.com/docs/5.3/
- **Chart.js** : https://www.chartjs.org/docs/

---

**Bon courage dans votre apprentissage ! 🚀**

