"""
Point d'entrée Vercel pour Django
Ce fichier est utilisé par Vercel pour router toutes les requêtes vers Django
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent.parent / 'backend'
backend_path = str(backend_dir.resolve())

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configurer les variables d'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Importer l'application WSGI Django
from django.core.wsgi import get_wsgi_application

# Initialiser l'application Django
django_app = get_wsgi_application()

# Exporter l'application pour Vercel
# Vercel cherche 'handler' ou 'app', pas 'application'
handler = django_app
app = django_app

