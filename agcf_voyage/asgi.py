"""
ASGI config for agcf_voyage project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

application = get_asgi_application()

