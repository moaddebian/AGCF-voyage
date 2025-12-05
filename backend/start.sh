#!/bin/bash
# Script de démarrage pour Railway
set -e

echo "🔧 Installation des dépendances..."
cd /app/backend || cd backend
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🚀 Démarrage de Gunicorn..."
exec python -m gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120

