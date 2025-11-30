#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Détection et ajout automatique de l'environnement virtuel au sys.path
def setup_virtualenv():
    """Configure automatiquement l'environnement virtuel s'il existe."""
    project_root = Path(__file__).parent.parent
    venv_site_packages = project_root / 'venv' / 'Lib' / 'site-packages'
    
    if venv_site_packages.exists():
        # Ajouter le site-packages de l'environnement virtuel au début de sys.path
        venv_path = str(venv_site_packages)
        if venv_path not in sys.path:
            sys.path.insert(0, venv_path)

# Configurer l'environnement virtuel avant d'importer Django
setup_virtualenv()

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

