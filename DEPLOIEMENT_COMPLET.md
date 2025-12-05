# 🚀 GUIDE DE DÉPLOIEMENT COMPLET
## Architecture : Railway + Cloudinary + Vercel + Resend

---

## 📋 TABLE DES MATIÈRES

1. [Architecture du déploiement](#architecture)
2. [Préparation du projet](#preparation)
3. [Étape 1 : Configuration PostgreSQL](#etape1)
4. [Étape 2 : Configuration Cloudinary](#etape2)
5. [Étape 3 : Configuration Resend](#etape3)
6. [Étape 4 : Déploiement Railway (Backend)](#etape4)
7. [Étape 5 : Déploiement Vercel (Frontend)](#etape5)
8. [Configuration finale](#finale)
9. [Vérification et tests](#verification)

---

## 🏗️ ARCHITECTURE DU DÉPLOIEMENT

```
┌─────────────────┐
│   Utilisateur   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Vercel      │  ← Frontend (HTML, CSS, JS statiques)
│  (Frontend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Railway      │  ← Backend Django (API)
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬─────────────┐
    ▼         ▼              ▼             ▼
┌────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐
│PostgreSQL│ │Cloudinary│ │ Resend  │ │  ...   │
│  (DB)   │ │ (Médias)  │ │(Emails) │ │        │
└────────┘ └──────────┘ └─────────┘ └────────┘
```

**Services utilisés :**
- **Railway** : Backend Django + Base de données PostgreSQL
- **Cloudinary** : Stockage des billets PDF et fichiers médias
- **Vercel** : Hébergement des fichiers statiques (optionnel, peut aussi servir via Railway)
- **Resend** : Envoi d'emails transactionnels

---

## 🔧 PRÉPARATION DU PROJET

### Étape 0.1 : Mettre à jour les dépendances

Ajoutez ces packages à `backend/requirements.txt` :

```txt
Django>=5.2.8
Pillow>=10.2.0
reportlab==4.0.7
qrcode==7.4.2
django-crispy-forms>=2.5
crispy-bootstrap5>=2025.6
python-dateutil==2.8.2
psycopg2-binary>=2.9.9  # Pour PostgreSQL (remplace PyMySQL)
dj-database-url>=2.2.0
gunicorn>=21.2.0
whitenoise>=6.7.0
cloudinary>=1.36.0  # Pour Cloudinary
django-cloudinary-storage>=0.3.0  # Intégration Django-Cloudinary
resend>=0.6.0  # Pour Resend
python-dotenv>=1.0.0  # Pour les variables d'environnement
```

---

## 📦 ÉTAPE 1 : CONFIGURATION POSTGRESQL

### 1.1 : Modifier `backend/requirements.txt`

Remplacez `PyMySQL` par `psycopg2-binary` (déjà fait ci-dessus).

### 1.2 : Modifier `backend/agcf_voyage/settings.py`

Mettez à jour la configuration de la base de données :

```python
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Configuration de la base de données
database_url = os.environ.get('DATABASE_URL')

# Si DATABASE_URL est définie, l'utiliser (priorité) - Pour Railway PostgreSQL
if database_url and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600, ssl_require=True)
    }
# Sinon, utiliser la configuration par défaut (développement local)
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',  # Changé de mysql à postgresql
            'NAME': os.environ.get('DB_NAME', 'agcf_voyage'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
```

### 1.3 : Supprimer la référence PyMySQL

Dans `backend/agcf_voyage/__init__.py`, supprimez ou commentez :

```python
# Support pour PyMySQL (plus nécessaire avec PostgreSQL)
# import pymysql
# pymysql.install_as_MySQLdb()
```

---

## ☁️ ÉTAPE 2 : CONFIGURATION CLOUDINARY

### 2.1 : Créer un compte Cloudinary

1. Allez sur https://cloudinary.com/users/register/free
2. Créez un compte gratuit (25GB de stockage)
3. Notez vos identifiants depuis le Dashboard :
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

### 2.2 : Modifier `backend/agcf_voyage/settings.py`

Ajoutez la configuration Cloudinary :

```python
# Cloudinary Configuration
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)

# Configuration des fichiers médias avec Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Garder MEDIA_URL pour les URLs Cloudinary
MEDIA_URL = '/media/'  # Cloudinary gère les URLs automatiquement
```

### 2.3 : Modifier `backend/reservations/utils.py`

Mettez à jour la fonction `generer_billet_pdf()` pour uploader sur Cloudinary :

```python
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

def generer_billet_pdf(reservation):
    """Génère un billet PDF premium et l'upload sur Cloudinary"""
    # ... (code existant pour générer le PDF) ...
    
    # Générer le PDF localement d'abord
    output_dir = os.path.join(settings.MEDIA_ROOT, 'billets')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'billet_{reservation.code_reservation}.pdf')
    
    # ... (code existant pour créer le PDF) ...
    doc.build(story)
    
    # Uploader sur Cloudinary
    try:
        upload_result = upload(
            pdf_path,
            folder="billets",
            resource_type="raw",  # Pour les PDFs
            public_id=f"billet_{reservation.code_reservation}",
            overwrite=True
        )
        # Obtenir l'URL Cloudinary
        cloudinary_pdf_url, _ = cloudinary_url(
            f"billets/billet_{reservation.code_reservation}",
            resource_type="raw"
        )
        
        # Optionnel : supprimer le fichier local après upload
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        return cloudinary_pdf_url  # Retourner l'URL Cloudinary au lieu du chemin local
    except Exception as e:
        # En cas d'erreur, garder le fichier local
        print(f"Erreur upload Cloudinary: {e}")
        return pdf_path
```

### 2.4 : Modifier les vues qui utilisent les PDFs

Dans `backend/reservations/views.py`, mettez à jour `telecharger_billet()` :

```python
@login_required
def telecharger_billet(request, code):
    """Téléchargement du billet PDF depuis Cloudinary"""
    reservation = get_object_or_404(Reservation, code_reservation=code, utilisateur=request.user)
    
    if reservation.statut != 'confirmee':
        messages.error(request, "Cette réservation n'est pas confirmée.")
        return redirect('reservations:detail_reservation', code=code)
    
    try:
        # Générer le PDF (qui sera uploadé sur Cloudinary)
        pdf_url = generer_billet_pdf(reservation)
        
        # Si c'est une URL Cloudinary, rediriger
        if pdf_url.startswith('http'):
            return redirect(pdf_url)
        
        # Sinon, servir le fichier local (fallback)
        with open(pdf_url, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="billet_{reservation.code_reservation}.pdf"'
            return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du billet : {str(e)}")
        return redirect('reservations:detail_reservation', code=code)
```

---

## 📧 ÉTAPE 3 : CONFIGURATION RESEND

### 3.1 : Créer un compte Resend

1. Allez sur https://resend.com
2. Créez un compte gratuit (3000 emails/mois)
3. Créez une API Key depuis le Dashboard
4. Vérifiez votre domaine (optionnel mais recommandé)

### 3.2 : Modifier `backend/agcf_voyage/settings.py`

Ajoutez la configuration Resend :

```python
# Resend Email Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'  # Toujours 'resend' pour Resend
EMAIL_HOST_PASSWORD = RESEND_API_KEY  # Utiliser l'API key comme mot de passe
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@votredomaine.com')  # Doit être un domaine vérifié
DEFAULT_FROM_EMAIL = EMAIL_FROM
```

### 3.3 : Modifier `backend/reservations/utils.py`

Mettez à jour `envoyer_billet_email()` pour utiliser Resend :

```python
def envoyer_billet_email(reservation, pdf_path_or_url, est_modification=False):
    """Envoie le billet par email avec Resend"""
    utilisateur = reservation.utilisateur
    
    # ... (code HTML existant) ...
    
    sujet = f'{"Votre billet modifié" if est_modification else "Votre billet"} AGCF Voyages'
    
    # Si pdf_path_or_url est une URL Cloudinary, télécharger le PDF
    if pdf_path_or_url.startswith('http'):
        import requests
        pdf_response = requests.get(pdf_path_or_url)
        pdf_content = pdf_response.content
    else:
        # Fichier local
        with open(pdf_path_or_url, 'rb') as pdf:
            pdf_content = pdf.read()
    
    email = EmailMessage(
        subject=sujet,
        body=html_body,
        from_email=settings.EMAIL_FROM,
        to=[reservation.utilisateur.email],
    )
    email.content_subtype = 'html'
    
    # Attacher le PDF
    email.attach(
        f'billet_{reservation.code_reservation}.pdf',
        pdf_content,
        'application/pdf'
    )
    
    email.send()
```

---

## 🚂 ÉTAPE 4 : DÉPLOIEMENT RAILWAY (BACKEND)

### 4.1 : Créer un compte Railway

1. Allez sur https://railway.app
2. Connectez-vous avec GitHub
3. Créez un nouveau projet

### 4.2 : Ajouter PostgreSQL

1. Dans votre projet Railway, cliquez sur **"+ New"**
2. Sélectionnez **"Database"** → **"Add PostgreSQL"**
3. Railway créera automatiquement une base PostgreSQL
4. Notez la variable `DATABASE_URL` depuis les variables d'environnement

### 4.3 : Créer `railway.json` (optionnel)

Créez `railway.json` à la racine du projet :

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4.4 : Créer `Procfile` (pour Railway)

Créez `Procfile` à la racine du projet :

```
web: cd backend && gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 4.5 : Créer `runtime.txt` (optionnel, pour spécifier Python)

Créez `runtime.txt` à la racine :

```
python-3.11.0
```

### 4.6 : Créer `nixpacks.toml` (configuration Railway)

Créez `nixpacks.toml` à la racine :

```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = [
    "cd backend",
    "pip install -r requirements.txt",
    "python manage.py collectstatic --noinput"
]

[start]
cmd = "cd backend && gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:$PORT --workers 2"
```

### 4.7 : Déployer sur Railway

1. Dans Railway, cliquez sur **"+ New"** → **"GitHub Repo"**
2. Sélectionnez votre repository
3. Railway détectera automatiquement Django
4. Ajoutez les variables d'environnement :

```
DJANGO_DEBUG=False
SECRET_KEY=votre-secret-key-genere-aleatoirement
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
DATABASE_URL=postgresql://... (automatiquement ajouté par Railway)
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
RESEND_API_KEY=votre-resend-api-key
EMAIL_FROM=noreply@votredomaine.com
CSRF_TRUSTED_ORIGINS=https://votre-app.railway.app
```

### 4.8 : Migrations et Superuser

1. Dans Railway, allez dans votre service Django
2. Cliquez sur **"Deploy"** → **"View Logs"**
3. Ouvrez un terminal Railway (ou utilisez Railway CLI) :

```bash
# Installer Railway CLI
npm i -g @railway/cli

# Se connecter
railway login

# Lier au projet
railway link

# Exécuter les migrations
railway run python backend/manage.py migrate

# Créer un superuser
railway run python backend/manage.py createsuperuser
```

---

## ⚡ ÉTAPE 5 : DÉPLOIEMENT VERCEL (FRONTEND STATIQUE - OPTIONNEL)

**Note** : Vercel peut servir les fichiers statiques, mais Railway peut aussi le faire avec WhiteNoise. Cette étape est optionnelle.

### 5.1 : Créer `vercel.json`

Créez `vercel.json` à la racine :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/frontend/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "https://votre-app.railway.app/$1"
    }
  ]
}
```

### 5.2 : Alternative - Utiliser WhiteNoise sur Railway

Si vous préférez tout héberger sur Railway, WhiteNoise est déjà configuré dans votre `settings.py`. Assurez-vous que :

```python
STATIC_ROOT = FRONTEND_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Et dans `backend/agcf_voyage/urls.py` :

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos URLs ...
]

# Servir les fichiers statiques en production
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

---

## ✅ CONFIGURATION FINALE

### Variables d'environnement à configurer

**Sur Railway :**

```bash
# Django
DJANGO_DEBUG=False
SECRET_KEY=<générer-une-clé-secrète>
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
CSRF_TRUSTED_ORIGINS=https://votre-app.railway.app

# Base de données (automatique avec Railway PostgreSQL)
DATABASE_URL=postgresql://...

# Cloudinary
CLOUDINARY_CLOUD_NAME=<votre-cloud-name>
CLOUDINARY_API_KEY=<votre-api-key>
CLOUDINARY_API_SECRET=<votre-api-secret>

# Resend
RESEND_API_KEY=<votre-resend-api-key>
EMAIL_FROM=noreply@votredomaine.com

# Optionnel : autres
TIME_ZONE=Europe/Paris
LANGUAGE_CODE=fr
```

### Générer une SECRET_KEY

```python
# Dans un terminal Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🧪 VÉRIFICATION ET TESTS

### 1. Vérifier la base de données

```bash
railway run python backend/manage.py dbshell
```

### 2. Vérifier les migrations

```bash
railway run python backend/manage.py showmigrations
```

### 3. Tester l'upload Cloudinary

Créez une réservation et vérifiez que le PDF est uploadé sur Cloudinary.

### 4. Tester l'envoi d'email

Créez une réservation et vérifiez que l'email est envoyé via Resend.

### 5. Vérifier les fichiers statiques

Visitez `https://votre-app.railway.app/static/admin/css/base.css` pour vérifier que WhiteNoise fonctionne.

---

## 📝 CHECKLIST DE DÉPLOIEMENT

- [ ] ✅ Mise à jour `requirements.txt` avec PostgreSQL, Cloudinary, Resend
- [ ] ✅ Configuration PostgreSQL dans `settings.py`
- [ ] ✅ Configuration Cloudinary dans `settings.py`
- [ ] ✅ Modification `generer_billet_pdf()` pour uploader sur Cloudinary
- [ ] ✅ Configuration Resend dans `settings.py`
- [ ] ✅ Modification `envoyer_billet_email()` pour utiliser Resend
- [ ] ✅ Création compte Railway et PostgreSQL
- [ ] ✅ Création compte Cloudinary
- [ ] ✅ Création compte Resend
- [ ] ✅ Déploiement sur Railway
- [ ] ✅ Configuration variables d'environnement
- [ ] ✅ Exécution des migrations
- [ ] ✅ Création superuser
- [ ] ✅ Tests fonctionnels

---

## 🆘 DÉPANNAGE

### Erreur : "No module named 'psycopg2'"

```bash
# Ajoutez dans requirements.txt
psycopg2-binary>=2.9.9
```

### Erreur : "Cloudinary upload failed"

Vérifiez vos clés API Cloudinary dans les variables d'environnement.

### Erreur : "Email not sent"

Vérifiez que votre domaine est vérifié sur Resend et que `EMAIL_FROM` correspond.

### Erreur : "Static files not found"

Exécutez :
```bash
railway run python backend/manage.py collectstatic --noinput
```

---

## 🎉 FÉLICITATIONS !

Votre application Django est maintenant déployée avec :
- ✅ Backend sur Railway
- ✅ Base de données PostgreSQL sur Railway
- ✅ Fichiers médias sur Cloudinary
- ✅ Emails via Resend
- ✅ Fichiers statiques via WhiteNoise (ou Vercel)

**Votre site est en ligne ! 🚀**

