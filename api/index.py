"""
Handler Vercel pour l'application Django AGCF Voyages

Ce fichier sert de point d'entrée pour Vercel Serverless Functions.
Vercel détecte automatiquement Python et utilise cette application WSGI.
"""
import os
import sys
from pathlib import Path

try:
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
    # Vercel cherche 'app' ou 'application' automatiquement
    app = get_wsgi_application()
    
except Exception as e:
    # Si erreur, créer un handler qui affiche l'erreur
    import traceback
    error_msg = f"Error initializing Django: {str(e)}\n\n{traceback.format_exc()}"
    
    def app(environ, start_response):
        """Handler d'erreur pour afficher le problème"""
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]

