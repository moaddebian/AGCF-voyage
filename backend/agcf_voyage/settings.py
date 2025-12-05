"""
Django settings for agcf_voyage project.
"""

from pathlib import Path
import os

# Charger les variables d'environnement depuis .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv n'est pas installé, continuer sans

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to backend/
PROJECT_ROOT = BASE_DIR.parent  # Points to project root (AGCF/)
FRONTEND_DIR = PROJECT_ROOT / 'frontend'  # Points to frontend/


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-agcf-voyage-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Configuration ALLOWED_HOSTS
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
else:
    # Par défaut pour le développement local
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Configuration CSRF_TRUSTED_ORIGINS
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()]
else:
    # Par défaut pour le développement local
    CSRF_TRUSTED_ORIGINS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'cloudinary_storage',  # Pour Cloudinary (doit être avant 'django.contrib.staticfiles')
    'cloudinary',  # Pour Cloudinary
    'reservations',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agcf_voyage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [FRONTEND_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'agcf_voyage.wsgi.application'


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

# Configuration SQLite (pour développement local - décommentez pour utiliser)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('ar', 'العربية'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# CSRF settings pour permettre l'accès JavaScript au token
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [FRONTEND_DIR / 'static']
STATIC_ROOT = FRONTEND_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = FRONTEND_DIR / 'media'

# Cloudinary Configuration (pour stockage des médias en production)
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('df0c3lvlx', ''),
        'API_KEY': os.environ.get('771282459579441', ''),
        'API_SECRET': os.environ.get('psW0mqjrl97hSXeYAt-YgSziVFQ', ''),
    }
    
    # Configurer Cloudinary seulement si les credentials sont fournis
    if all([CLOUDINARY_STORAGE['CLOUD_NAME'], CLOUDINARY_STORAGE['API_KEY'], CLOUDINARY_STORAGE['API_SECRET']]):
        cloudinary.config(
            cloud_name=CLOUDINARY_STORAGE['df0c3lvlx'],
            api_key=CLOUDINARY_STORAGE['771282459579441'],
            api_secret=CLOUDINARY_STORAGE['psW0mqjrl97hSXeYAt-YgSziVFQ'],
        )
        # Utiliser Cloudinary pour les fichiers médias en production
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        # MEDIA_URL sera géré automatiquement par Cloudinary
except ImportError:
    # Cloudinary non installé, utiliser le stockage local
    pass

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'reservations:dashboard'
LOGOUT_REDIRECT_URL = 'reservations:home'

# Email settings (pour l'envoi de billets)
# Configuration Resend (pour production)
RESEND_API_KEY = os.environ.get('re_BBvNeWKM_5Bt8njhGeFQcTYdEt3pbUVpV', '')

if RESEND_API_KEY:
    # Utiliser Resend en production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.resend.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'resend'  # Toujours 'resend' pour Resend
    EMAIL_HOST_PASSWORD = re_BBvNeWKM_5Bt8njhGeFQcTYdEt3pbUVpV  # Utiliser l'API key comme mot de passe
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'onboarding@resend.dev')
    DEFAULT_FROM_EMAIL = EMAIL_FROM
else:
    # Utiliser console backend en développement
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    DEFAULT_FROM_EMAIL = 'noreply@agcf-voyages.com'
