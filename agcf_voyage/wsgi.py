"""
WSGI config for agcf_voyage project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

application = get_wsgi_application()

# Expose app for Vercel
app = application

