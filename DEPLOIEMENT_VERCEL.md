# 🚀 Guide de Déploiement Django sur Vercel

## 📋 Prérequis

1. **Compte Vercel** : Créez un compte sur [vercel.com](https://vercel.com)
2. **GitHub** : Votre projet doit être sur GitHub
3. **Base de données** : Vous aurez besoin d'une base de données MySQL externe (PlanetScale, Railway, ou autre)

---

## 📦 ÉTAPE 1 : Préparer les fichiers de configuration

### 1.1 Créer `vercel.json` à la racine du projet

Ce fichier configure Vercel pour servir votre application Django.

### 1.2 Créer `api/index.py`

Ce fichier sera le point d'entrée pour Vercel (Serverless Function).

### 1.3 Mettre à jour `requirements.txt`

Ajouter les dépendances nécessaires pour Vercel.

---

## 🔧 ÉTAPE 2 : Configuration des fichiers

### Fichier 1 : `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/media/(.*)",
      "dest": "/media/$1"
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.14"
  }
}
```

### Fichier 2 : `api/index.py`

```python
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Handler pour Vercel
def handler(request):
    from django.http import HttpResponse
    from django.core.handlers.wsgi import WSGIHandler
    
    # Convertir la requête Vercel en requête Django
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', '0'),
        'SERVER_NAME': request.headers.get('host', 'localhost'),
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Ajouter les headers HTTP
    for key, value in request.headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Créer le handler WSGI
    wsgi_handler = WSGIHandler()
    response = wsgi_handler(environ, lambda status, headers: None)
    
    # Retourner la réponse
    return HttpResponse(
        response.content,
        status=response.status_code,
        content_type=response.get('Content-Type', 'text/html')
    )
```

**Note** : Cette approche peut nécessiter des ajustements. Une alternative plus simple est d'utiliser `vercel-wsgi`.

---

## 🔄 ÉTAPE 3 : Alternative simplifiée avec `vercel-wsgi`

### 3.1 Installer `vercel-wsgi`

Ajoutez à `backend/requirements.txt` :
```
vercel-wsgi>=0.1.0
```

### 3.2 Créer `api/index.py` (version simplifiée)

```python
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Importer et retourner l'application WSGI
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

# Export pour Vercel
from vercel_wsgi import VercelWSGI
handler = VercelWSGI(app)
```

---

## ⚙️ ÉTAPE 4 : Configuration des variables d'environnement

Dans Vercel Dashboard → Settings → Environment Variables, ajoutez :

### Variables obligatoires :

```
SECRET_KEY=votre-secret-key-tres-long-et-aleatoire
DJANGO_DEBUG=False
ALLOWED_HOSTS=votre-domaine.vercel.app,www.votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://votre-domaine.vercel.app,https://www.votre-domaine.com
DATABASE_URL=mysql://user:password@host:port/database_name
```

### Variables optionnelles :

```
DB_NAME=agcf_voyage
DB_USER=votre_user
DB_PASSWORD=votre_password
DB_HOST=votre_host
DB_PORT=3306
EMAIL_HOST_USER=votre_email
EMAIL_HOST_PASSWORD=votre_password_email
```

---

## 📁 ÉTAPE 5 : Structure des fichiers

Votre structure devrait ressembler à :

```
AGCF/
├── api/
│   └── index.py          # Handler Vercel
├── backend/              # Votre application Django
│   ├── accounts/
│   ├── reservations/
│   ├── agcf_voyage/
│   └── manage.py
├── frontend/             # Templates et statiques
│   ├── templates/
│   └── static/
├── vercel.json           # Configuration Vercel
└── requirements.txt     # Dépendances Python
```

---

## 🗄️ ÉTAPE 6 : Configuration de la base de données

### Option 1 : PlanetScale (Recommandé pour MySQL)

1. Créez un compte sur [planetscale.com](https://planetscale.com)
2. Créez une nouvelle base de données
3. Récupérez l'URL de connexion
4. Ajoutez-la comme `DATABASE_URL` dans Vercel

### Option 2 : Railway

1. Créez un compte sur [railway.app](https://railway.app)
2. Créez un service MySQL
3. Récupérez l'URL de connexion
4. Ajoutez-la comme `DATABASE_URL` dans Vercel

---

## 📤 ÉTAPE 7 : Déploiement

### 7.1 Via GitHub (Recommandé)

1. **Poussez votre code sur GitHub** :
```bash
git add .
git commit -m "Préparation pour déploiement Vercel"
git push origin main
```

2. **Connectez Vercel à GitHub** :
   - Allez sur [vercel.com/new](https://vercel.com/new)
   - Importez votre repository GitHub
   - Vercel détectera automatiquement Django

3. **Configurez le projet** :
   - **Root Directory** : `/` (racine du projet)
   - **Build Command** : `cd backend && python manage.py collectstatic --noinput`
   - **Output Directory** : `backend` (ou laissez vide)
   - **Install Command** : `pip install -r backend/requirements.txt`

4. **Ajoutez les variables d'environnement** (étape 4)

5. **Déployez** : Cliquez sur "Deploy"

### 7.2 Via CLI Vercel

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel

# Déployer en production
vercel --prod
```

---

## 🔧 ÉTAPE 8 : Configuration Django pour Vercel

### Modifier `backend/agcf_voyage/settings.py`

Ajoutez cette section à la fin du fichier :

```python
# Configuration pour Vercel
import os

# Détecter si on est sur Vercel
IS_VERCEL = os.environ.get('VERCEL', False)

if IS_VERCEL:
    # Configuration spécifique Vercel
    DEBUG = False
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
    CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    
    # Fichiers statiques avec WhiteNoise (déjà configuré)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Fichiers média : utiliser un stockage cloud (S3, Cloudinary, etc.)
    # Pour l'instant, on désactive le stockage local
    # Vous devrez configurer un stockage cloud pour les billets PDF
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## 📦 ÉTAPE 9 : Gestion des fichiers média (Billets PDF)

**IMPORTANT** : Vercel est serverless, les fichiers locaux ne persistent pas.

### Option 1 : AWS S3 (Recommandé)

1. Installez `django-storages` :
```bash
pip install django-storages boto3
```

2. Ajoutez à `settings.py` :
```python
INSTALLED_APPS = [
    # ...
    'storages',
]

# Configuration S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'
```

3. Ajoutez les variables dans Vercel :
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
AWS_S3_REGION_NAME=us-east-1
```

### Option 2 : Cloudinary (Plus simple)

1. Installez `cloudinary` :
```bash
pip install cloudinary django-cloudinary-storage
```

2. Ajoutez à `settings.py` :
```python
INSTALLED_APPS = [
    # ...
    'cloudinary',
    'cloudinary_storage',
]

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
```

---

## 🧪 ÉTAPE 10 : Tests après déploiement

1. **Vérifiez que le site charge** : `https://votre-projet.vercel.app`
2. **Testez la page d'accueil**
3. **Testez la recherche de trains**
4. **Testez la création de compte**
5. **Testez une réservation** (vérifiez que les PDFs sont générés)

---

## 🐛 Résolution de problèmes

### Erreur : "Module not found"

- Vérifiez que `requirements.txt` contient toutes les dépendances
- Vérifiez que le chemin dans `api/index.py` est correct

### Erreur : "Database connection failed"

- Vérifiez que `DATABASE_URL` est correcte dans Vercel
- Vérifiez que la base de données accepte les connexions externes

### Erreur : "Static files not found"

- Exécutez `python manage.py collectstatic` localement
- Vérifiez que WhiteNoise est configuré

### Erreur : "CSRF verification failed"

- Vérifiez `CSRF_TRUSTED_ORIGINS` dans les variables d'environnement
- Ajoutez votre domaine Vercel

---

## 📝 Checklist finale

- [ ] Fichier `vercel.json` créé
- [ ] Fichier `api/index.py` créé
- [ ] `requirements.txt` mis à jour
- [ ] Variables d'environnement configurées dans Vercel
- [ ] Base de données externe configurée
- [ ] Stockage cloud configuré pour les fichiers média
- [ ] Code poussé sur GitHub
- [ ] Projet connecté à Vercel
- [ ] Déploiement réussi
- [ ] Tests fonctionnels effectués

---

## 🎉 Félicitations !

Votre application Django est maintenant déployée sur Vercel !

**Prochaines étapes** :
- Configurez un domaine personnalisé
- Configurez les emails (SendGrid, Mailgun, etc.)
- Configurez le monitoring (Sentry, etc.)

