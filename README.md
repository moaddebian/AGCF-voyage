# AGCF Voyages - Système de Réservation de Trains

AGCF Voyages est une application web complète de réservation de billets de train développée avec Django. Le système permet aux utilisateurs de rechercher, réserver et gérer leurs billets de train de manière intuitive et sécurisée.

## Fonctionnalités principales

### 🏠 Page d'accueil
- Interface moderne et claire avec barre de recherche
- Sélection de la gare de départ et d'arrivée
- Sélection de la date et de l'heure de départ
- Affichage des offres spéciales

### 🔍 Recherche de trains
- Affichage des trains disponibles selon les critères de recherche
- Informations détaillées : heure de départ/arrivée, durée, classe, prix
- Filtres par classe, prix et horaire
- Pagination des résultats

### 👤 Gestion de compte utilisateur
- Inscription et création de compte
- Connexion/Déconnexion
- Modification des informations personnelles
- Suppression de compte
- Gestion des cartes de réduction

### 🎫 Réservation et paiement
- Réservation de billets avec sélection du nombre de places
- Application de cartes de réduction
- Ajout des informations des passagers
- Paiement en ligne (simulation - carte bancaire, PayPal)
- Génération automatique du billet PDF

### 📊 Tableau de bord
- Vue d'ensemble des réservations
- Statistiques personnelles
- Accès rapide aux dernières réservations
- Gestion complète des billets

### 🎁 Offres et promotions
- Consultation des offres spéciales
- Affichage des réductions disponibles
- Notifications personnalisées

### 📄 Billets électroniques
- Génération de billets PDF professionnels
- Code QR pour contrôle à l'embarquement
- Envoi automatique par email
- Téléchargement depuis l'espace utilisateur

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
```bash
cd AGCF
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
   - Sur Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Sur Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Effectuer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur (pour accéder à l'admin)**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

8. **Accéder à l'application**
   - Application: http://127.0.0.1:8000/
   - Administration: http://127.0.0.1:8000/admin/

## Configuration des données initiales

Pour tester l'application, vous devez créer des données de test (gares, trains, etc.) via l'interface d'administration Django.

### Exemple de données à créer:

1. **Gares**: Créer plusieurs gares marocaines (ex: Casa-Voyageurs, Rabat-Ville, Fès-Ville, Marrakech)
2. **Trains**: Créer des trains avec leurs horaires et prix (Al Boraq, trains classiques)
3. **Cartes de réduction**: Créer différents types de cartes (Jeune, Senior, etc.)
4. **Offres promotionnelles**: Créer des offres spéciales

**Note**: La commande `init_data` crée automatiquement 10 gares marocaines et 12 trains avec des trajets réalistes.

## Structure du projet

```
AGCF/
├── agcf_voyage/          # Configuration du projet Django
│   ├── settings.py       # Paramètres du projet
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuration WSGI
├── reservations/         # Application principale de réservation
│   ├── models.py         # Modèles de données
│   ├── views.py          # Vues de l'application
│   ├── forms.py          # Formulaires
│   ├── urls.py           # URLs de l'application
│   ├── admin.py          # Configuration admin
│   └── utils.py          # Utilitaires (PDF, email)
├── accounts/             # Application de gestion des comptes
│   ├── models.py         # Modèles utilisateurs
│   ├── views.py          # Vues d'authentification
│   ├── forms.py          # Formulaires utilisateurs
│   └── urls.py           # URLs d'authentification
├── templates/             # Templates HTML
│   ├── base.html         # Template de base
│   ├── reservations/     # Templates de réservation
│   └── accounts/         # Templates d'authentification
├── static/               # Fichiers statiques (CSS, JS, images)
├── media/                # Fichiers média (billets PDF, images)
├── manage.py             # Script de gestion Django
└── requirements.txt      # Dépendances Python
```

## Fonctionnalités techniques

### Modèles de données
- **Gare**: Gares de départ et d'arrivée
- **Train**: Informations sur les trains (horaires, prix, places)
- **Reservation**: Réservations des utilisateurs
- **Passager**: Informations des passagers
- **CarteReduction**: Types de cartes de réduction
- **CarteReductionUtilisateur**: Cartes associées aux utilisateurs
- **OffrePromotion**: Offres et promotions

### Sécurité
- Authentification Django intégrée
- Protection CSRF
- Validation des formulaires
- Gestion sécurisée des mots de passe

### Génération de PDF
- Utilisation de ReportLab
- Code QR intégré
- Design professionnel
- Informations complètes du billet

### Email
- Envoi automatique des billets
- Configuration via settings.py
- Support console pour le développement

## Personnalisation

### Configuration email
Pour activer l'envoi d'emails réels, modifiez `agcf_voyage/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
```

### Intégration de paiement
Actuellement, le système simule le paiement. Pour une intégration réelle:
- Stripe: https://stripe.com/docs/payments
- PayPal: https://developer.paypal.com/docs/api/overview/

## Développement

### Commandes utiles
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Collecter les fichiers statiques (production)
python manage.py collectstatic
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à:
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Optimiser le code

## Licence

Ce projet est fourni à des fins éducatives et de démonstration.

## Support

Pour toute question ou problème, veuillez créer une issue sur le dépôt du projet.

---

**Développé avec ❤️ en utilisant Django**

