# 📚 EXPLICATION COMPLÈTE DU PROJET AGCF VOYAGES

## 🎯 Vue d'ensemble
**AGCF Voyages** est une application web Django complète pour la réservation de billets de train. Elle permet aux utilisateurs de rechercher, réserver et gérer leurs voyages, tandis que les administrateurs peuvent gérer les trains, les réservations et analyser les revenus.

---

## 📁 PARTIE 1 : BACKEND (Django)

### 🗂️ Structure du dossier `backend/`

```
backend/
├── accounts/          # Application de gestion des comptes utilisateurs
├── reservations/      # Application principale de réservation
├── agcf_voyage/      # Configuration principale du projet Django
├── manage.py         # Script de gestion Django
└── requirements.txt  # Dépendances Python
```

---

### 1️⃣ **Dossier `agcf_voyage/`** - Configuration principale

#### 📄 `settings.py` - Configuration Django
**Rôle** : Fichier central de configuration du projet

**Points clés** :
- **Base de données** : MySQL (production) ou SQLite (développement)
  - Utilise `dj-database-url` pour la configuration via variables d'environnement
  - Supporte les connexions distantes avec SSL
- **Langues** : Multilingue (Français, Anglais, Arabe)
- **Fichiers statiques** : Configuration pour CSS, JS, images
  - `STATICFILES_DIRS` : `frontend/static/`
  - `STATIC_ROOT` : `frontend/staticfiles/` (pour production)
  - `MEDIA_ROOT` : `frontend/media/` (billets PDF, images)
- **Applications installées** :
  - `django.contrib.admin` : Interface d'administration
  - `crispy_forms` + `crispy_bootstrap5` : Formulaires stylisés
  - `reservations` : Application principale
  - `accounts` : Gestion des utilisateurs
- **Sécurité** :
  - `SECRET_KEY` depuis variables d'environnement
  - `DEBUG` configurable
  - `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` configurables
- **Middleware** :
  - `WhiteNoise` : Servir les fichiers statiques en production
  - `LocaleMiddleware` : Gestion multilingue
  - `CsrfViewMiddleware` : Protection CSRF

#### 📄 `urls.py` - Routage principal
**Rôle** : Définit toutes les URLs du projet

**Routes principales** :
- `/admin/analytics/` : Analyse des revenus et passagers (admin)
- `/admin/analytics/data/` : API JSON pour les graphiques
- `/admin/` : Interface d'administration Django
- `/i18n/setlang/` : Changement de langue
- `/` : Routes de l'app `reservations`
- `/accounts/` : Routes de l'app `accounts`

#### 📄 `fix_python314.py` - Correctif Python 3.14
**Rôle** : Patch pour compatibilité Django avec Python 3.14.0
- Corrige l'erreur `AttributeError: 'super' object has no attribute 'dicts'`
- Importé automatiquement dans `__init__.py`

#### 📄 `wsgi.py` - Interface WSGI
**Rôle** : Point d'entrée pour déploiement (serveurs web comme Gunicorn)

---

### 2️⃣ **Dossier `accounts/`** - Gestion des utilisateurs

#### 📄 `models.py` - Modèles de données
**`ProfilUtilisateur`** :
- Extension du modèle `User` de Django
- Champs : téléphone, adresse, ville, code postal, date de naissance
- Relation `OneToOne` avec `User`

#### 📄 `forms.py` - Formulaires
**Formulaires définis** :
- `InscriptionForm` : Création de compte
- `ModifierProfilForm` : Modification du profil
- `CarteReductionForm` : Ajout de carte de réduction

#### 📄 `views.py` - Vues (logique métier)
**Fonctions principales** :
1. **`inscription(request)`** :
   - Crée un nouvel utilisateur
   - Connecte automatiquement après inscription
   - Redirige vers le dashboard

2. **`profil(request)`** :
   - Affiche/modifie le profil utilisateur
   - Liste les cartes de réduction associées
   - Nécessite une authentification (`@login_required`)

3. **`ajouter_carte_reduction(request)`** :
   - Permet d'ajouter une carte de réduction au profil
   - Vérifie la validité de la carte

4. **`supprimer_carte_reduction(request, carte_id)`** :
   - Supprime une carte de réduction

5. **`supprimer_compte(request)`** :
   - Supprime définitivement le compte utilisateur
   - Nécessite une confirmation POST

6. **`deconnexion(request)`** :
   - Déconnecte l'utilisateur
   - Accepte GET et POST (contrairement à `LogoutView` standard)

#### 📄 `urls.py` - Routes de l'application
**Routes définies** :
- `/accounts/inscription/` → `inscription`
- `/accounts/connexion/` → `LoginView` (Django)
- `/accounts/deconnexion/` → `deconnexion`
- `/accounts/profil/` → `profil`
- `/accounts/ajouter-carte/` → `ajouter_carte_reduction`
- `/accounts/supprimer-carte/<id>/` → `supprimer_carte_reduction`
- `/accounts/supprimer-compte/` → `supprimer_compte`

#### 📄 `admin.py` - Interface d'administration
**Rôle** : Personnalisation de l'admin Django pour les modèles `accounts`

---

### 3️⃣ **Dossier `reservations/`** - Application principale

#### 📄 `models.py` - Modèles de données (CŒUR DU SYSTÈME)

**1. `Gare`** :
- Représente une gare ferroviaire
- Champs : nom, ville, code (unique), adresse
- Utilisé comme point de départ/arrivée des trains

**2. `Train`** :
- Représente un train
- Champs :
  - `numero` : Numéro unique du train
  - `gare_depart` / `gare_arrivee` : Gares de départ et d'arrivée
  - `heure_depart` / `heure_arrivee` : Horaires
  - `duree` : Durée du trajet
  - `classe` : 1ère ou 2ème classe
  - `prix_base` : Prix de base du billet
  - `places_disponibles` : Nombre de places restantes
  - `nombre_voitures` : Nombre de voitures dans le train
  - `actif` : Train disponible ou non
- **Méthodes importantes** :
  - `est_en_maintenance()` : Vérifie si le train est en maintenance
  - `get_gares_intermediaires()` : Retourne toutes les gares du trajet
  - `passe_par_gare()` : Vérifie si le train passe par une gare

**3. `ArretIntermediaire`** :
- Représente un arrêt entre le départ et l'arrivée
- Champs : train, gare, ordre, heure_passage
- Permet aux trains de passer par plusieurs gares

**4. `CarteReduction`** :
- Types de cartes de réduction disponibles
- Champs : type (jeune, senior, famille, weekend), nom, pourcentage de réduction
- Exemple : "Carte Jeune" avec 30% de réduction

**5. `CarteReductionUtilisateur`** :
- Carte de réduction associée à un utilisateur
- Champs : utilisateur, carte, numéro_carte, date_expiration
- **Limitations** :
  - Maximum 2 utilisations par jour
  - Doit être valide (non expirée)
- **Méthodes** :
  - `peut_utiliser_aujourdhui()` : Vérifie la limite quotidienne
  - `est_valide()` : Vérifie la date d'expiration

**6. `Reservation`** :
- **MODÈLE PRINCIPAL** : Représente une réservation
- Champs :
  - `utilisateur` : Qui a réservé
  - `train` : Train réservé
  - `date_voyage` : Date du voyage
  - `nombre_places` : Nombre de passagers
  - `carte_reduction` : Carte utilisée (optionnelle)
  - `prix_unitaire` : Prix par place
  - `reduction_appliquee` : Montant de la réduction
  - `prix_total` : Prix final après réduction
  - `statut` : en_attente, confirmee, annulee, utilisee
  - `mode_paiement` : carte, paypal, cheque
  - `code_reservation` : Code unique (ex: "ABC123")
- **Méthode** : `calculer_prix_total()` : Calcule le prix avec réduction

**7. `Passager`** :
- Informations des passagers pour une réservation
- Champs : nom, prénom, date de naissance
- Relation : Plusieurs passagers par réservation

**8. `OffrePromotion`** :
- Offres promotionnelles temporaires
- Champs : titre, description, pourcentage de réduction, dates de validité
- Méthode : `est_valide()` : Vérifie si l'offre est active

**9. `RetardTrain`** :
- Suivi des retards déclarés
- Champs : train, date_voyage, minutes_retard, motif, statut
- Permet de signaler et gérer les retards

**10. `MaintenanceTrain`** :
- Planification de la maintenance
- Champs : train, type_maintenance, dates, statut, responsable
- Empêche la réservation pendant la maintenance

#### 📄 `views.py` - Vues (logique métier)

**Vues principales** :

1. **`home(request)`** :
   - Page d'accueil avec formulaire de recherche
   - Affiche les offres promotionnelles actives
   - Traite la recherche et redirige vers les résultats

2. **`recherche_resultats(request, ...)`** :
   - Affiche les trains disponibles selon les critères
   - Filtre par : gare départ, gare arrivée, date, heure (optionnelle)
   - Gère les gares intermédiaires
   - Exclut les trains en maintenance ou sans places

3. **`reserver_train(request, train_id)`** :
   - Page de réservation d'un train
   - Calcule le prix avec réduction si carte disponible
   - Ajoute au panier (session)

4. **`ajouter_passagers(request)`** :
   - Formulaire pour ajouter les informations des passagers
   - Stocke dans la session

5. **`panier(request)`** :
   - Affiche le contenu du panier
   - Permet de modifier/supprimer des réservations
   - Calcule le total

6. **`paiement(request)`** :
   - Traite le paiement
   - Crée les réservations en base de données
   - Génère les codes de réservation uniques
   - Génère les billets PDF

7. **`confirmation(request, code)`** :
   - Page de confirmation après paiement
   - Affiche les détails de la réservation

8. **`mes_reservations(request)`** :
   - Liste toutes les réservations de l'utilisateur connecté
   - Permet de voir les détails, annuler, télécharger le billet

9. **`detail_reservation(request, code)`** :
   - Détails complets d'une réservation
   - Affichage du billet

10. **`annuler_reservation(request, code)`** :
    - Annule une réservation
    - Change le statut à "annulée"

11. **`telecharger_billet(request, code)`** :
    - Télécharge le billet PDF

12. **`gerer_reservation_public(request)`** :
    - Permet de retrouver une réservation sans être connecté
    - Utilise le code de réservation

13. **`dashboard(request)`** :
    - Tableau de bord utilisateur
    - Statistiques personnelles

14. **`offres_promotions(request)`** :
    - Liste toutes les offres promotionnelles actives

15. **`gestion_retards(request)`** :
    - Interface admin pour gérer les retards

16. **`gestion_maintenance(request)`** :
    - Interface admin pour gérer les maintenances

#### 📄 `forms.py` - Formulaires
**Formulaires définis** :
- `RechercheTrainForm` : Recherche de trains
- `FiltreTrainForm` : Filtres avancés
- `ReservationForm` : Formulaire de réservation
- `PassagerForm` : Informations passagers
- `PaiementForm` : Informations de paiement
- `GestionReservationForm` : Gestion de réservation
- `AnnulationReservationForm` : Annulation
- `ReprogrammationReservationForm` : Reprogrammation
- `RetardTrainForm` : Signalement de retard
- `MaintenanceTrainForm` : Planification maintenance

#### 📄 `utils.py` - Fonctions utilitaires
**Fonctions principales** :
- `generer_billet_pdf(reservation)` : Génère un PDF de billet avec QR code
- `envoyer_billet_email(reservation)` : Envoie le billet par email
- `envoyer_notif_retard(reservation, minutes)` : Notifie d'un retard

#### 📄 `admin_analytics.py` - Analyse pour l'admin
**Rôle** : Analyse des revenus et volume de passagers

**Fonctionnalités** :
- **Analyse des revenus** :
  - Graphique d'évolution des revenus
  - Vue quotidienne, hebdomadaire, mensuelle
  - Prédictions IA (tendances)
- **Analyse du volume de passagers** :
  - Nombre de passagers par jour
  - Graphique en barres
  - Statistiques (total, moyenne, évolution)
- **Périodes** : 7, 30, 90, 365 jours ou toutes
- **API JSON** : `/admin/analytics/data/` pour les graphiques Chart.js

#### 📄 `urls.py` - Routes de l'application
**Routes principales** :
- `/` → `home`
- `/recherche/...` → `recherche_resultats`
- `/reserver/<train_id>/` → `reserver_train`
- `/ajouter-passagers/` → `ajouter_passagers`
- `/paiement/` → `paiement`
- `/confirmation/<code>/` → `confirmation`
- `/mes-reservations/` → `mes_reservations`
- `/reservation/<code>/` → `detail_reservation`
- `/reservation/<code>/annuler/` → `annuler_reservation`
- `/telecharger-billet/<code>/` → `telecharger_billet`
- `/gerer-reservation/` → `gerer_reservation_public`
- `/dashboard/` → `dashboard`
- `/offres/` → `offres_promotions`
- `/retards/` → `gestion_retards` (admin)
- `/maintenance/` → `gestion_maintenance` (admin)

#### 📄 `admin.py` - Interface d'administration
**Rôle** : Personnalisation de l'admin Django
- Enregistre tous les modèles
- Personnalise l'affichage
- Ajoute des filtres et recherches

#### 📄 `management/commands/init_data.py`
**Rôle** : Commande Django pour initialiser des données de test
- Crée des gares, trains, cartes de réduction, etc.

---

### 4️⃣ **Fichiers racine `backend/`**

#### 📄 `manage.py` - Script de gestion Django
**Rôle** : Point d'entrée pour toutes les commandes Django
- **Particularité** : Détecte automatiquement l'environnement virtuel (`venv/`)
- Plus besoin d'activer manuellement le venv !

**Commandes courantes** :
- `python manage.py runserver` : Lance le serveur
- `python manage.py migrate` : Applique les migrations
- `python manage.py createsuperuser` : Crée un admin
- `python manage.py collectstatic` : Collecte les fichiers statiques

#### 📄 `requirements.txt` - Dépendances Python
**Packages principaux** :
- `Django>=5.2.8` : Framework web
- `Pillow>=10.2.0` : Traitement d'images
- `reportlab==4.0.7` : Génération de PDF
- `qrcode==7.4.2` : Génération de QR codes
- `django-crispy-forms>=2.5` : Formulaires stylisés
- `crispy-bootstrap5>=2025.6` : Thème Bootstrap 5
- `PyMySQL==1.1.0` : Driver MySQL pour Python
- `cryptography>=41.0.0` : Chiffrement
- `whitenoise>=6.7.0` : Servir les fichiers statiques
- `dj-database-url>=2.2.0` : Configuration DB via URL
- `gunicorn>=21.2.0` : Serveur WSGI pour production

---

## 📁 PARTIE 2 : FRONTEND (Templates & Static)

### 🗂️ Structure du dossier `frontend/`

```
frontend/
├── templates/        # Templates HTML Django
├── static/          # Fichiers statiques (CSS, JS, images)
└── media/           # Fichiers uploadés (billets PDF)
```

---

### 1️⃣ **Dossier `templates/`** - Templates HTML

#### 📄 `base.html` - Template de base
**Rôle** : Template principal hérité par tous les autres

**Sections principales** :

1. **En-tête (`<head>`)** :
   - Bootstrap 5.3.0 (CSS)
   - Bootstrap Icons
   - Chart.js (pour les graphiques admin)
   - Variables CSS personnalisées (couleurs, gradients)

2. **Navigation (`<nav>`)** :
   - Barre de navigation sticky
   - Logo AGCF Voyages
   - Menu : Accueil, Recherche, Panier, Profil
   - Sélecteur de langue (FR/EN/AR)
   - Dropdown utilisateur (Profil, Déconnexion)

3. **Messages** :
   - Affiche les messages Django (succès, erreur, info)

4. **Contenu principal** :
   - `{% block content %}` : Contenu spécifique à chaque page

5. **Pied de page** :
   - Informations de contact
   - Liens utiles

6. **Scripts** :
   - Bootstrap JS
   - Scripts personnalisés
   - Traduction JavaScript

**Styles CSS personnalisés** :
- Variables CSS (couleurs, gradients, ombres)
- Animations (pulse, hover)
- Cards professionnelles
- Boutons avec gradients
- Responsive design

#### 📁 `templates/accounts/` - Templates de comptes

**1. `inscription.html`** :
- Formulaire d'inscription
- Champs : nom, prénom, email, mot de passe, confirmation
- Design professionnel avec Bootstrap 5

**2. `connexion.html`** :
- Formulaire de connexion
- Lien vers inscription
- Design cohérent avec le reste

**3. `profil.html`** :
- Affichage du profil utilisateur
- Formulaire de modification
- Liste des cartes de réduction
- Boutons pour ajouter/supprimer des cartes

**4. `ajouter_carte_reduction.html`** :
- Formulaire pour ajouter une carte de réduction
- Sélection du type de carte
- Saisie du numéro et date d'expiration

**5. `supprimer_compte.html`** :
- Confirmation de suppression de compte
- Formulaire POST pour sécurité

#### 📁 `templates/reservations/` - Templates de réservation

**1. `home.html`** :
- Page d'accueil
- Formulaire de recherche de trains
- Affichage des offres promotionnelles
- Design attractif avec hero section

**2. `recherche_resultats.html`** :
- Liste des trains disponibles
- Filtres (prix, heure, classe)
- Affichage des détails (durée, prix, places)
- Bouton "Réserver" pour chaque train

**3. `reserver_train.html`** :
- Détails du train sélectionné
- Sélection du nombre de places
- Application automatique de la carte de réduction
- Calcul du prix total

**4. `ajouter_passagers.html`** :
- Formulaire pour chaque passager
- Champs : nom, prénom, date de naissance
- Validation côté client

**5. `panier.html`** :
- Liste des réservations en panier
- Modification/suppression
- Total général
- Bouton "Procéder au paiement"

**6. `paiement.html`** :
- Formulaire de paiement
- Sélection du mode de paiement
- Récapitulatif de la commande
- Validation finale

**7. `confirmation.html`** :
- Page de confirmation
- Code de réservation
- Détails du voyage
- Bouton de téléchargement du billet

**8. `mes_reservations.html`** :
- Liste de toutes les réservations de l'utilisateur
- Filtres par statut
- Actions : Voir détails, Annuler, Télécharger

**9. `detail_reservation.html`** :
- Détails complets d'une réservation
- Informations du train
- Liste des passagers
- QR code du billet
- Actions disponibles

**10. `annuler_reservation.html`** :
- Confirmation d'annulation
- Formulaire avec motif (optionnel)

**11. `gerer_reservation.html`** :
- Recherche de réservation par code
- Affichage des détails
- Actions possibles (sans connexion)

**12. `dashboard.html`** :
- Tableau de bord utilisateur
- Statistiques personnelles
- Réservations récentes

**13. `offres_promotions.html`** :
- Liste des offres promotionnelles
- Cards avec images
- Dates de validité

**14. `retards.html`** :
- Interface admin pour gérer les retards
- Liste des retards signalés
- Formulaire de signalement

**15. `maintenance.html`** :
- Interface admin pour gérer les maintenances
- Liste des maintenances planifiées
- Formulaire de planification

#### 📁 `templates/admin/` - Templates admin

**1. `analytics.html`** :
- Dashboard d'analyse pour l'admin
- Graphiques Chart.js :
  - Revenus (ligne)
  - Volume de passagers (barres)
- Sélecteurs de période (7, 30, 90, 365 jours, toutes)
- Sélecteurs de vue (quotidienne, hebdomadaire, mensuelle)
- Statistiques (total, moyenne, évolution)
- Prédictions IA
- **Particularité** : Textes en noir avec `!important` pour visibilité

**2. `base.html`** :
- Template de base pour l'admin
- Bouton flottant AI (boule orange)
- Modal pour l'analyse
- Intégration avec l'admin Django

---

### 2️⃣ **Dossier `static/`** - Fichiers statiques

#### 📁 `static/admin/css/`

**`admin_custom.css`** :
- Styles personnalisés pour l'admin Django
- Personnalisation des couleurs et layout

#### 📁 `static/admin/js/`

**1. `ai_floating_button.js`** :
- Gère le bouton flottant AI dans l'admin
- Ouvre le modal d'analyse
- Charge les données via AJAX depuis `/admin/analytics/data/`
- Initialise les graphiques Chart.js
- Gère les sélecteurs de période et vue
- Affiche les icônes dans les selects

**2. `train_duree_auto.js`** :
- Calcul automatique de la durée d'un train
- Utilisé dans l'admin lors de la création/modification d'un train

#### 📁 `static/images/`

**`logo-agcf.jpg`** :
- Logo de l'entreprise AGCF Voyages
- Utilisé dans la navbar

---

### 3️⃣ **Dossier `media/`** - Fichiers uploadés

#### 📁 `media/billets/`
- Contient tous les billets PDF générés
- Nommage : `billet_<CODE>.pdf`
- Générés par `reportlab` avec QR code

---

## 🔄 FLUX DE DONNÉES

### Exemple : Processus de réservation

1. **Recherche** (`home.html` → `home()`)
   - Utilisateur remplit le formulaire
   - POST vers `/`
   - Redirection vers `/recherche/...`

2. **Résultats** (`recherche_resultats.html` → `recherche_resultats()`)
   - Affichage des trains disponibles
   - Filtrage par maintenance, places, etc.

3. **Réservation** (`reserver_train.html` → `reserver_train()`)
   - Sélection d'un train
   - Calcul du prix avec réduction
   - Ajout au panier (session)

4. **Passagers** (`ajouter_passagers.html` → `ajouter_passagers()`)
   - Saisie des informations passagers
   - Stockage en session

5. **Panier** (`panier.html` → `panier()`)
   - Vérification du contenu
   - Modification possible

6. **Paiement** (`paiement.html` → `paiement()`)
   - Sélection du mode de paiement
   - POST vers `/paiement/`
   - Création des réservations en DB
   - Génération des billets PDF
   - Envoi par email (optionnel)

7. **Confirmation** (`confirmation.html` → `confirmation()`)
   - Affichage du code de réservation
   - Téléchargement du billet

---

## 🔐 SÉCURITÉ

### Mesures implémentées :
1. **Authentification** : Système de connexion Django
2. **Autorisations** : `@login_required` pour les pages protégées
3. **CSRF Protection** : Tokens CSRF sur tous les formulaires
4. **Validation** : Validation côté serveur et client
5. **Sessions** : Stockage sécurisé des données temporaires
6. **SQL Injection** : Protection via ORM Django
7. **XSS** : Échappement automatique dans les templates

---

## 🌐 MULTILINGUE

### Langues supportées :
- **Français** (par défaut)
- **Anglais**
- **Arabe**

### Implémentation :
- `LocaleMiddleware` activé
- Fichiers de traduction dans `locale/`
- Sélecteur de langue dans la navbar
- Traduction JavaScript pour les éléments dynamiques

---

## 📊 ANALYTICS & IA

### Fonctionnalités d'analyse :
1. **Revenus** :
   - Évolution quotidienne/hebdomadaire/mensuelle
   - Prédictions de tendances
   - Statistiques (total, moyenne, évolution %)

2. **Volume de passagers** :
   - Nombre de passagers par jour
   - Graphiques en barres
   - Statistiques similaires

3. **Interface** :
   - Bouton flottant dans l'admin
   - Modal avec graphiques Chart.js
   - Sélecteurs de période et vue
   - API JSON pour les données

---

## 🚀 DÉPLOIEMENT

### Configuration production :
- Variables d'environnement pour :
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `DEBUG=False`
  - `ALLOWED_HOSTS`
- `WhiteNoise` pour servir les fichiers statiques
- `Gunicorn` comme serveur WSGI
- `collectstatic` pour rassembler les fichiers statiques

---

## 📝 COMMANDES UTILES

```bash
# Lancer le serveur
python backend/manage.py runserver

# Appliquer les migrations
python backend/manage.py migrate

# Créer un superutilisateur
python backend/manage.py createsuperuser

# Collecter les fichiers statiques
python backend/manage.py collectstatic

# Initialiser les données de test
python backend/manage.py init_data
```

---

## 🎨 DESIGN

### Palette de couleurs :
- **Primaire** : `#1a1a2e` (bleu foncé)
- **Secondaire** : `#ff6600` (orange)
- **Accent** : `#ff8533` (orange clair)
- **Succès** : `#00c853` (vert)
- **Cream** : `#f8f9fa` (beige clair)

### Caractéristiques :
- Design moderne et professionnel
- Responsive (mobile, tablette, desktop)
- Animations fluides
- Cards avec ombres
- Boutons avec gradients
- Typographie claire

---

## ✅ CONCLUSION

Ce projet est une **application complète de réservation de trains** avec :
- ✅ Gestion complète des utilisateurs
- ✅ Système de réservation avancé
- ✅ Gestion des cartes de réduction
- ✅ Génération de billets PDF avec QR codes
- ✅ Interface d'administration complète
- ✅ Analytics avec prédictions IA
- ✅ Multilingue (FR/EN/AR)
- ✅ Design professionnel et responsive
- ✅ Sécurité renforcée
- ✅ Gestion des retards et maintenances

**Technologies utilisées** : Django 5.2.8, MySQL, Bootstrap 5, Chart.js, ReportLab, QRCode, Python 3.14.0

