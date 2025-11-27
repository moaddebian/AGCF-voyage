import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agcf_voyage.settings")

application = get_wsgi_application()
# Alias for @vercel/python
app = application
