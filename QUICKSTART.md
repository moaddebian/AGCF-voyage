# Guide de démarrage rapide - AGCF Voyages

## Installation rapide

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Créer un superutilisateur
```bash
python manage.py createsuperuser
```
Suivez les instructions pour créer un compte administrateur.

### 4. Initialiser les données de test
```bash
python manage.py init_data
```
Cette commande crée automatiquement :
- 6 gares (Paris, Lyon, Marseille, Bordeaux, Nantes)
- 8 trains avec différents horaires
- 4 types de cartes de réduction
- 3 offres promotionnelles

### 5. Lancer le serveur
```bash
python manage.py runserver
```

### 6. Accéder à l'application
- **Application principale**: http://127.0.0.1:8000/
- **Interface d'administration**: http://127.0.0.1:8000/admin/

## Première utilisation

### En tant qu'administrateur
1. Connectez-vous à l'interface d'administration : http://127.0.0.1:8000/admin/
2. Utilisez les identifiants du superutilisateur créé
3. Vous pouvez gérer toutes les données (gares, trains, réservations, etc.)

### En tant qu'utilisateur
1. Allez sur la page d'accueil : http://127.0.0.1:8000/
2. Cliquez sur "Inscription" pour créer un compte
3. Remplissez le formulaire d'inscription
4. Une fois connecté, vous pouvez :
   - Rechercher des trains
   - Réserver des billets
   - Gérer vos réservations
   - Ajouter des cartes de réduction
   - Consulter les offres

## Test d'une réservation complète

1. **Rechercher votre voyage**
   - Sur la page d'accueil, sélectionnez :
     - Gare de départ : Casablanca (Casa-Voyageurs)
     - Gare d'arrivée : Rabat (Rabat-Ville)
     - Date de départ : une date future
   - Cliquez sur "Rechercher"

2. **Réserver un train**
   - Choisissez un train dans les résultats
   - Cliquez sur "Réserver"
   - Sélectionnez le nombre de places et une carte de réduction (optionnel)
   - Cliquez sur "Continuer"

3. **Ajouter les passagers**
   - Remplissez les informations pour chaque passager
   - Cliquez sur "Continuer vers le paiement"

4. **Payer**
   - Choisissez un mode de paiement
   - Remplissez les informations (simulation)
   - Cliquez sur "Confirmer le paiement"

5. **Télécharger le billet**
   - Après confirmation, vous pouvez télécharger le billet PDF
   - Le billet est également envoyé par email (console en développement)

## Structure des données de test

### Gares marocaines créées
- Casa-Voyageurs (Casablanca)
- Casa-Port (Casablanca)
- Rabat-Ville (Rabat)
- Rabat-Agdal (Rabat)
- Fès-Ville (Fès)
- Marrakech (Marrakech)
- Tanger-Ville (Tanger)
- Meknès-Ville (Meknès)
- Oujda (Oujda)
- Agadir (Agadir)

### Trains créés (Al Boraq et trains classiques)
- ALB-1001 : Casablanca → Rabat (6h00, 1ère classe, 45.00 MAD)
- ALB-1002 : Casablanca → Rabat (8h30, 2ème classe, 35.00 MAD)
- ALB-2001 : Casablanca → Fès (7h00, 1ère classe, 95.00 MAD)
- ALB-2002 : Casablanca → Fès (14h00, 2ème classe, 75.00 MAD)
- ALB-3001 : Casablanca → Marrakech (8h00, 1ère classe, 120.00 MAD)
- ALB-3002 : Casablanca → Marrakech (15h30, 2ème classe, 90.00 MAD)
- ALB-4001 : Rabat → Tanger (9h00, 1ère classe, 110.00 MAD)
- ALB-4002 : Rabat → Tanger (16h00, 2ème classe, 85.00 MAD)
- TRN-5001 : Fès → Meknès (10h00, 2ème classe, 25.00 MAD)
- TRN-6001 : Casablanca → Oujda (6h30, 1ère classe, 150.00 MAD)
- TRN-6002 : Casablanca → Oujda (14h00, 2ème classe, 120.00 MAD)
- TRN-7001 : Casablanca → Agadir (7h30, 2ème classe, 130.00 MAD)

### Cartes de réduction
- Carte Jeune : -30%
- Carte Senior : -25%
- Carte Famille : -20%
- Carte Weekend : -15%

## Commandes utiles

```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Réinitialiser les données de test
python manage.py init_data

# Accéder au shell Django
python manage.py shell

# Voir les URLs disponibles
python manage.py show_urls  # (nécessite django-extensions)

# Collecter les fichiers statiques (production)
python manage.py collectstatic
```

## Dépannage

### Erreur : "No module named 'crispy_forms'"
```bash
pip install -r requirements.txt
```

### Erreur : "Table doesn't exist"
```bash
python manage.py migrate
```

### Erreur lors de la génération de PDF
Vérifiez que les dossiers `media/billets/` existent. Ils seront créés automatiquement lors de la première génération.

### Les emails ne sont pas envoyés
En développement, les emails sont affichés dans la console. Pour activer l'envoi réel, configurez les paramètres email dans `agcf_voyage/settings.py`.

## Prochaines étapes

1. Personnalisez les templates selon vos besoins
2. Configurez l'envoi d'emails réels
3. Intégrez un système de paiement réel (Stripe, PayPal)
4. Ajoutez des fonctionnalités supplémentaires
5. Déployez en production

---

**Bon développement ! 🚂**

