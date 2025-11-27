# Backend - AGCF Voyages

Ce dossier contient toute la logique backend de l'application Django.

## Structure

```
backend/
├── agcf_voyage/          # Configuration du projet Django
│   ├── settings.py       # Paramètres du projet
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuration WSGI
├── reservations/         # Application principale de réservation
│   ├── models.py         # Modèles de données
│   ├── views.py          # Vues de l'application
│   └── ...
├── accounts/             # Application de gestion des comptes
│   ├── models.py         # Modèles utilisateurs
│   ├── views.py          # Vues d'authentification
│   └── ...
├── manage.py            # Script de gestion Django
└── requirements.txt     # Dépendances Python
```

## Commandes principales

Toutes les commandes Django doivent être exécutées depuis ce dossier :

```bash
cd backend
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
python manage.py init_data
```

## Configuration

Les fichiers statiques et templates sont situés dans le dossier `../frontend/` et sont automatiquement référencés dans `settings.py`.

