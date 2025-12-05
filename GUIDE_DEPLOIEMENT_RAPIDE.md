# 🚀 Guide de Déploiement Rapide - Vercel

## ✅ Fichiers créés

Les fichiers suivants ont été créés pour le déploiement :

1. ✅ `vercel.json` - Configuration Vercel
2. ✅ `api/index.py` - Handler WSGI pour Vercel
3. ✅ `api/__init__.py` - Package Python
4. ✅ `.vercelignore` - Fichiers à ignorer
5. ✅ `requirements.txt` - Dépendances (pointe vers backend/requirements.txt)
6. ✅ `DEPLOIEMENT_VERCEL.md` - Guide complet détaillé

## 📋 Étapes de déploiement

### ÉTAPE 1 : Préparer votre base de données

**Option A : PlanetScale (Recommandé - MySQL gratuit)**
1. Créez un compte sur [planetscale.com](https://planetscale.com)
2. Créez une nouvelle base de données
3. Récupérez l'URL de connexion (format : `mysql://user:password@host:port/database`)

**Option B : Railway (MySQL)**
1. Créez un compte sur [railway.app](https://railway.app)
2. Créez un service MySQL
3. Récupérez l'URL de connexion

### ÉTAPE 2 : Pousser votre code sur GitHub

```bash
git add .
git commit -m "Configuration pour déploiement Vercel"
git push origin main
```

### ÉTAPE 3 : Connecter Vercel à GitHub

1. Allez sur [vercel.com/new](https://vercel.com/new)
2. Cliquez sur "Import Git Repository"
3. Sélectionnez votre repository GitHub
4. Vercel détectera automatiquement Django

### ÉTAPE 4 : Configurer le projet dans Vercel

**Settings du projet :**
- **Framework Preset** : Other
- **Root Directory** : `/` (racine)
- **Build Command** : `cd backend && python manage.py collectstatic --noinput`
- **Output Directory** : (laisser vide)
- **Install Command** : `pip install -r backend/requirements.txt`

### ÉTAPE 5 : Ajouter les variables d'environnement

Dans Vercel Dashboard → Settings → Environment Variables, ajoutez :

#### Variables OBLIGATOIRES :

```
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DJANGO_DEBUG=False
ALLOWED_HOSTS=votre-projet.vercel.app
CSRF_TRUSTED_ORIGINS=https://votre-projet.vercel.app
DATABASE_URL=mysql://user:password@host:port/database
```

**Générer SECRET_KEY :**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

#### Variables OPTIONNELLES :

```
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### ÉTAPE 6 : Migrer la base de données

**Option A : Via Vercel CLI (Recommandé)**

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Lier le projet
vercel link

# Exécuter les migrations
vercel env pull .env.local
cd backend
python manage.py migrate
```

**Option B : Via une base de données locale puis export/import**

1. Exécutez les migrations localement
2. Exportez les données
3. Importez dans votre base de données cloud

### ÉTAPE 7 : Créer un superutilisateur

```bash
# Via Vercel CLI
vercel env pull .env.local
cd backend
python manage.py createsuperuser
```

### ÉTAPE 8 : Déployer

1. Cliquez sur "Deploy" dans Vercel Dashboard
2. Attendez la fin du build (2-5 minutes)
3. Votre site sera disponible sur `https://votre-projet.vercel.app`

## ⚠️ Points importants

### 1. Fichiers média (Billets PDF)

**PROBLÈME** : Vercel est serverless, les fichiers locaux ne persistent pas.

**SOLUTION** : Vous devez configurer un stockage cloud (S3, Cloudinary, etc.)

Voir `DEPLOIEMENT_VERCEL.md` section "Gestion des fichiers média" pour les détails.

### 2. Collectstatic

Les fichiers statiques sont collectés automatiquement lors du build.
WhiteNoise est déjà configuré dans votre projet.

### 3. Python 3.14

Vercel supporte Python 3.14, mais si vous rencontrez des problèmes,
vous pouvez forcer Python 3.12 dans `vercel.json` :
```json
"env": {
  "PYTHON_VERSION": "3.12"
}
```

## 🧪 Tester après déploiement

1. ✅ Page d'accueil charge
2. ✅ Recherche de trains fonctionne
3. ✅ Inscription/Connexion fonctionne
4. ✅ Réservation fonctionne (sans génération PDF pour l'instant)
5. ✅ Admin Django accessible

## 🐛 Résolution de problèmes

### Erreur : "Module not found"
→ Vérifiez que toutes les dépendances sont dans `backend/requirements.txt`

### Erreur : "Database connection failed"
→ Vérifiez `DATABASE_URL` dans les variables d'environnement

### Erreur : "CSRF verification failed"
→ Ajoutez votre domaine dans `CSRF_TRUSTED_ORIGINS`

### Erreur : "Static files not found"
→ Vérifiez que `collectstatic` s'exécute lors du build

## 📞 Support

- Documentation Vercel : https://vercel.com/docs
- Documentation Django : https://docs.djangoproject.com
- Guide complet : Voir `DEPLOIEMENT_VERCEL.md`

## 🎉 C'est tout !

Votre application Django est maintenant prête à être déployée sur Vercel !

