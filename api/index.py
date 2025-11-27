import os
import sys
from pathlib import Path

# Ensure the backend package is on the Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Default Django settings module for the Vercel environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agcf_voyage.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
# Vercel's Python runtime looks for an ``app`` variable
app = application
