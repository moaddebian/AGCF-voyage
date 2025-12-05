# Dockerfile pour Django sur Railway
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements.txt
COPY backend/requirements.txt /app/backend/requirements.txt

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /app/backend/requirements.txt

# Copier le code de l'application
COPY . /app/

# Collecter les fichiers statiques
RUN cd /app/backend && python manage.py collectstatic --noinput

# Exposer le port
EXPOSE $PORT

# Commande de démarrage
CMD cd /app/backend && python -m gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

