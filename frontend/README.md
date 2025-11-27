# Frontend - AGCF Voyages

Ce dossier contient tous les fichiers frontend de l'application.

## Structure

```
frontend/
├── templates/           # Templates HTML Django
│   ├── base.html        # Template de base
│   ├── accounts/        # Templates d'authentification
│   └── reservations/    # Templates de réservation
├── static/              # Fichiers statiques (CSS, JS, images)
│   └── images/          # Images du site
├── media/               # Fichiers média uploadés par les utilisateurs
│   └── billets/         # Billets PDF générés
└── staticfiles/         # Fichiers statiques collectés (généré automatiquement)
```

## Notes

- Les templates sont automatiquement chargés par Django depuis `settings.py`
- Les fichiers statiques sont servis en développement via Django
- Les fichiers média sont stockés ici et servis via Django en développement
- Pour la production, utilisez `python manage.py collectstatic` depuis le dossier `backend/`

