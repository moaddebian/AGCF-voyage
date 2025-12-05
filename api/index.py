"""
Handler Vercel pour l'application Django AGCF Voyages

Ce fichier sert de point d'entrée pour Vercel Serverless Functions.
Vercel utilise @vercel/python qui convertit automatiquement les requêtes HTTP
en format WSGI compatible avec Django.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Détecter Vercel
os.environ['VERCEL'] = '1'

# Importer l'application WSGI Django
from django.core.wsgi import get_wsgi_application

# Initialiser l'application Django
application = get_wsgi_application()

# Vercel utilise automatiquement cette variable 'app' ou 'application'
# pour servir l'application WSGI

