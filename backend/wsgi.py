import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agcf_voyage.settings")

from agcf_voyage.wsgi import application as app

# Alias expected by @vercel/python
application = app
