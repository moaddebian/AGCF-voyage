@echo off
REM Script de démarrage du serveur Django
REM L'environnement virtuel est détecté automatiquement par manage.py
echo Démarrage du serveur AGCF Voyages...
cd backend
python manage.py runserver
pause

