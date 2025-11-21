# Guide de déploiement sur Vercel

Ce guide explique comment déployer votre application Django AGCF Voyages sur Vercel.

## Prérequis

1. Un compte Vercel (gratuit) : https://vercel.com
2. Le CLI Vercel installé (optionnel) : `npm i -g vercel`
3. Votre projet configuré avec Git

## Configuration

### 1. Fichiers de configuration

Les fichiers suivants ont été créés/modifiés pour le déploiement :

- **`vercel.json`** : Configuration Vercel pour le routage
- **`api/index.py`** : Handler serverless pour Django
- **`.vercelignore`** : Fichiers à exclure du déploiement
- **`requirements.txt`** : Inclut maintenant `whitenoise` pour les fichiers statiques

### 2. Variables d'environnement

Vous devez configurer les variables d'environnement suivantes dans Vercel :

#### Variables obligatoires :

```
SECRET_KEY=votre-secret-key-django-tres-securise
DEBUG=False
ALLOWED_HOSTS=votre-domaine.vercel.app,*.vercel.app
```

#### Variables de base de données (MySQL) :

```
DB_NAME=agcf_voyage
DB_USER=votre_utilisateur_mysql
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=votre_host_mysql
DB_PORT=3306
```

#### Variables email (optionnel) :

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
```

## Déploiement

### Option 1 : Via l'interface Vercel (recommandé)

1. **Connecter votre repository Git** :
   - Allez sur https://vercel.com
   - Cliquez sur "Add New Project"
   - Importez votre repository Git (GitHub, GitLab, Bitbucket)

2. **Configurer le projet** :
   - Framework Preset : **Other**
   - Root Directory : `.` (racine du projet)
   - Build Command : `python manage.py collectstatic --noinput`
   - Output Directory : `staticfiles` (ou laissez vide)

3. **Ajouter les variables d'environnement** :
   - Dans les paramètres du projet, allez dans "Environment Variables"
   - Ajoutez toutes les variables listées ci-dessus

4. **Déployer** :
   - Cliquez sur "Deploy"
   - Vercel va automatiquement détecter `vercel.json` et déployer votre application

### Option 2 : Via CLI Vercel

1. **Installer Vercel CLI** :
   ```bash
   npm i -g vercel
   ```

2. **Se connecter** :
   ```bash
   vercel login
   ```

3. **Déployer** :
   ```bash
   vercel
   ```

4. **Ajouter les variables d'environnement** :
   ```bash
   vercel env add SECRET_KEY
   vercel env add DEBUG
   vercel env add ALLOWED_HOSTS
   # ... etc pour toutes les variables
   ```

5. **Déployer en production** :
   ```bash
   vercel --prod
   ```

## Étapes post-déploiement

### 1. Exécuter les migrations

Vercel ne supporte pas directement les commandes Django. Vous avez deux options :

**Option A : Via Vercel CLI (recommandé)**
```bash
vercel env pull .env.local
python manage.py migrate
```

**Option B : Créer une fonction serverless pour les migrations**
Créez un fichier `api/migrate.py` (à utiliser avec prudence en production).

### 2. Créer un superutilisateur

Vous devrez créer un superutilisateur localement et l'importer, ou utiliser une fonction serverless temporaire.

### 3. Initialiser les données

Exécutez la commande `init_data` localement après avoir configuré la base de données :
```bash
python manage.py init_data
```

## Configuration de la base de données

Vercel ne fournit pas de base de données MySQL. Vous devez utiliser un service externe :

### Options recommandées :

1. **PlanetScale** (MySQL serverless) : https://planetscale.com
2. **Railway** : https://railway.app
3. **Aiven** : https://aiven.io
4. **AWS RDS** : https://aws.amazon.com/rds
5. **Google Cloud SQL** : https://cloud.google.com/sql

### Configuration avec PlanetScale (exemple) :

1. Créez un compte PlanetScale
2. Créez une base de données MySQL
3. Récupérez les informations de connexion
4. Configurez les variables d'environnement dans Vercel :
   ```
   DB_HOST=votre-host.planetscale.com
   DB_USER=votre-user
   DB_PASSWORD=votre-password
   DB_NAME=votre-database
   ```

## Fichiers statiques

Les fichiers statiques sont gérés par **WhiteNoise**, qui les sert directement depuis Django. Assurez-vous d'exécuter `collectstatic` avant le déploiement :

```bash
python manage.py collectstatic --noinput
```

## Limitations de Vercel

⚠️ **Important** : Vercel est une plateforme serverless avec certaines limitations :

1. **Pas de stockage persistant** : Les fichiers uploadés dans `/media` ne persisteront pas entre les déploiements
   - **Solution** : Utilisez un service de stockage cloud (AWS S3, Cloudinary, etc.)

2. **Timeout** : Les fonctions serverless ont un timeout (10s pour le plan gratuit, 60s pour Pro)
   - **Solution** : Optimisez vos requêtes et utilisez des tâches asynchrones si nécessaire

3. **Pas de commandes Django directes** : Vous ne pouvez pas exécuter `migrate`, `createsuperuser`, etc. directement
   - **Solution** : Utilisez le CLI Vercel ou créez des fonctions serverless temporaires

4. **Base de données** : Vercel ne fournit pas de base de données
   - **Solution** : Utilisez un service externe (voir section ci-dessus)

## Dépannage

### Erreur : "ModuleNotFoundError"
- Vérifiez que toutes les dépendances sont dans `requirements.txt`
- Vérifiez que `whitenoise` est installé

### Erreur : "DisallowedHost"
- Vérifiez que `ALLOWED_HOSTS` contient votre domaine Vercel
- Format : `votre-projet.vercel.app,*.vercel.app`

### Erreur : "Database connection failed"
- Vérifiez toutes les variables d'environnement de base de données
- Vérifiez que votre base de données accepte les connexions depuis l'extérieur
- Vérifiez les règles de firewall de votre base de données

### Les fichiers statiques ne se chargent pas
- Exécutez `python manage.py collectstatic` avant le déploiement
- Vérifiez que `STATIC_ROOT` est correctement configuré
- Vérifiez que WhiteNoise est dans `INSTALLED_APPS` et `MIDDLEWARE`

## Support

Pour plus d'informations :
- Documentation Vercel : https://vercel.com/docs
- Documentation Django sur Vercel : https://vercel.com/guides/deploying-django-with-vercel
- WhiteNoise : https://whitenoise.readthedocs.io

---

**Bon déploiement ! 🚀**

