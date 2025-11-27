# Guide de Déploiement sur Vercel

Ce guide vous explique comment déployer votre projet Django AGCF Voyages sur Vercel.

## 📋 Prérequis

1. Un compte Vercel (gratuit) : [https://vercel.com](https://vercel.com)
2. Un compte GitHub (pour connecter le dépôt)
3. Une base de données MySQL (locale ou cloud comme Railway, PlanetScale, etc.)

## 🚀 Étapes de Déploiement

### 1. Préparer le code

Assurez-vous que tous les fichiers sont commités :

```bash
git add .
git commit -m "Préparation pour déploiement Vercel"
git push origin main
```

### 2. Créer un projet sur Vercel

1. Allez sur [https://vercel.com](https://vercel.com) et connectez-vous
2. Cliquez sur **"New Project"**
3. Importez votre dépôt GitHub
4. Vercel détectera automatiquement la configuration depuis `vercel.json`

### 3. Configurer les Variables d'Environnement

Dans les **Settings** de votre projet Vercel, allez dans **Environment Variables** et ajoutez :

#### Variables Obligatoires :

```
SECRET_KEY=votre-clé-secrète-django-très-longue-et-aléatoire
DJANGO_SETTINGS_MODULE=agcf_voyage.settings
DJANGO_DEBUG=false
ALLOWED_HOSTS=votre-projet.vercel.app
CSRF_TRUSTED_ORIGINS=https://votre-projet.vercel.app
```

#### Configuration Base de Données :

**Option 1 : Utiliser DATABASE_URL (recommandé)**
```
DATABASE_URL=mysql://user:password@host:3306/dbname
```

**Option 2 : Utiliser les variables séparées**
```
DB_NAME=agcf_voyage
DB_USER=votre_user
DB_PASSWORD=votre_password
DB_HOST=votre_host
DB_PORT=3306
```

#### Configuration Email (optionnel) :

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### 4. Déployer

1. Cliquez sur **"Deploy"**
2. Attendez que le build se termine (peut prendre 2-5 minutes)
3. Votre application sera disponible à l'URL : `https://votre-projet.vercel.app`

### 5. Appliquer les Migrations

Après le premier déploiement, vous devez appliquer les migrations de base de données :

**Option A : Via Vercel CLI (recommandé)**

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Lier le projet
vercel link

# Récupérer les variables d'environnement
vercel env pull .env.local

# Appliquer les migrations
cd backend
python manage.py migrate
```

**Option B : Via un service externe**

Si votre base de données est accessible depuis votre machine locale :
```bash
cd backend
python manage.py migrate
```

### 6. Créer un Superutilisateur (Admin)

Pour accéder à l'interface d'administration Django :

```bash
cd backend
python manage.py createsuperuser
```

## 🔧 Configuration Post-Déploiement

### Ajouter un Domaine Personnalisé

1. Dans Vercel, allez dans **Settings** > **Domains**
2. Ajoutez votre domaine
3. Configurez les DNS selon les instructions Vercel
4. Mettez à jour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` dans les variables d'environnement
5. Redéployez

### Vérifier le Déploiement

- ✅ Accédez à `https://votre-projet.vercel.app` - la page d'accueil doit s'afficher
- ✅ Testez `/admin/` - l'interface d'administration doit fonctionner
- ✅ Vérifiez `/static/` - les fichiers statiques doivent se charger
- ✅ Testez un formulaire - le CSRF doit fonctionner

## 🐛 Dépannage

### Erreur : ModuleNotFoundError

Si vous voyez une erreur de module manquant :
1. Vérifiez que `requirements.txt` contient toutes les dépendances
2. Redéployez après avoir ajouté les dépendances manquantes

### Erreur : Database Connection

Si la connexion à la base de données échoue :
1. Vérifiez que `DATABASE_URL` ou les variables DB_* sont correctes
2. Vérifiez que votre base de données accepte les connexions depuis l'extérieur
3. Vérifiez les credentials

### Erreur : Static Files Not Found

Les fichiers statiques sont servis par WhiteNoise. Si vous avez des problèmes :
1. Vérifiez que `collectstatic` s'exécute correctement dans le build
2. Vérifiez que `STATIC_ROOT` pointe vers `frontend/staticfiles`

### Erreur : CSRF Token

Si vous avez des erreurs CSRF :
1. Vérifiez que `CSRF_TRUSTED_ORIGINS` contient votre domaine Vercel avec `https://`
2. Vérifiez que `ALLOWED_HOSTS` contient votre domaine

## 📝 Notes Importantes

- **Fichiers statiques** : Sont collectés automatiquement lors du build via `collectstatic`
- **Médias** : Les fichiers uploadés (comme les billets PDF) ne sont pas persistés sur Vercel. Utilisez un service de stockage externe (S3, Cloudinary, etc.) pour la production
- **Base de données** : Vercel ne fournit pas de base de données. Utilisez un service externe (Railway, PlanetScale, etc.)
- **Variables d'environnement** : Ne commitez JAMAIS vos secrets dans le code. Utilisez toujours les variables d'environnement Vercel

## 🔄 Déploiements Automatiques

Vercel déploie automatiquement à chaque `git push` sur la branche principale. Pour déployer manuellement :

```bash
vercel --prod
```

## 📞 Support

Pour plus d'aide :
- Documentation Vercel : [https://vercel.com/docs](https://vercel.com/docs)
- Documentation Django : [https://docs.djangoproject.com](https://docs.djangoproject.com)

