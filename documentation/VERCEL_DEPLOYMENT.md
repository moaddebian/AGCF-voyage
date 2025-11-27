# Déploiement Django sur Vercel

Ce guide décrit la préparation et le déploiement du projet sur Vercel avec `@vercel/python`.

## Instructions claires et directes
1) **Installer en local (optionnel pour vérifier)**
   ```bash
   git clone <votre-repo>
   cd AGCF-voyage
   pip install -r backend/requirements.txt
   cd backend && python manage.py collectstatic --noinput && cd ..
   ```
2) **Renseigner les variables Vercel** (Project Settings > Environment Variables)
   - `SECRET_KEY` : clé secrète Django.
   - `DJANGO_SETTINGS_MODULE=agcf_voyage.settings`
   - `DJANGO_DEBUG=false`
   - `ALLOWED_HOSTS=your-project.vercel.app,example.com`
   - `CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://example.com`
   - Base de données : `DATABASE_URL=mysql://user:pwd@host:3306/db` **ou** `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
3) **Pousser le code sur GitHub** (ou mettre à jour la branche suivie par Vercel)
   ```bash
   git add .
   git commit -m "Préparer déploiement Vercel"
   git push origin main
   ```
4) **Créer le projet sur Vercel**
   - Tableau de bord > **New Project** > **Import Git Repository**.
   - Racine `/` ; laissez les commandes auto-détectées par `vercel.json`.
5) **Déployer** : lancez le build. Les routes et la collecte des statiques sont gérées automatiquement par `vercel.json` et Whitenoise.
6) **Appliquer les migrations** (après le premier déploiement)
   ```bash
   vercel env pull .env.local   # optionnel pour tester localement
   cd backend
   python manage.py migrate
   ```
7) **Tester rapidement** : ouvrez l’URL Vercel, vérifiez les pages principales, les formulaires (CSRF) et `/static/*`.
8) **Ajouter un domaine personnalisé**
   - Vercel > Project > **Settings** > **Domains** > **Add** > saisir le domaine.
   - Configurer les DNS (CNAME `www` vers `cname.vercel-dns.com`, etc.).
   - Ajouter le domaine aux variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`, puis redéployer.

## Mode d'emploi express (checklist)
1. **Cloner le dépôt et installer les dépendances** :
   ```bash
   git clone <votre-repo>
   cd AGCF-voyage
   pip install -r backend/requirements.txt
   ```
2. **Configurer les secrets en local (facultatif, pratique pour tester)** : créez `backend/.env` et remplissez :
   ```env
   SECRET_KEY=replace_me
   DJANGO_SETTINGS_MODULE=agcf_voyage.settings
   DJANGO_DEBUG=false
   ALLOWED_HOSTS=your-project.vercel.app,example.com
   CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://example.com
   DATABASE_URL=mysql://user:password@host:3306/dbname  # ou variables MySQL équivalentes
   ```
3. **Vérifier les statiques** :
   ```bash
   cd backend
   python manage.py collectstatic --noinput
   ```
4. **Push vers GitHub** :
   ```bash
   git add .
   git commit -m "Préparer déploiement Vercel"
   git push origin main
   ```
5. **Connecter à Vercel** :
   - Tableau de bord Vercel > **New Project** > **Import Git Repository**.
   - Racine `/`, laissez les commandes par défaut (elles viennent de `vercel.json`).
6. **Définir les variables d'environnement dans Vercel** (Project Settings > Environment Variables) : copier celles de l'étape 2 avec vos vraies valeurs.
7. **Déployer** : lancez le déploiement. Après le premier déploiement, exécutez les migrations (cf. section « Préparer la base de données »).
8. **Domaine personnalisé** : ajoutez le domaine dans l'onglet **Domains**, configurez le DNS, puis ajoutez le domaine à `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`.

## Préparation de `settings.py`
- `DEBUG` : désactivé par défaut en production. Vous pouvez l'activer ponctuellement en définissant la variable d'environnement `DJANGO_DEBUG=true`.
- `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` : renseignez vos domaines Vercel et personnalisés via les variables d'environnement `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` (séparés par des virgules).
- Fichiers statiques : `whitenoise` est activé via le middleware et `STATICFILES_STORAGE` pour servir efficacement les assets.
- Base de données :
  - Par défaut MySQL via les variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
  - Pour une base externe type Railway/ElephantSQL/PlanetScale, définissez `DATABASE_URL` (format `scheme://user:password@host:port/db`) pour surcharger la configuration.

## Fichier `vercel.json`
- Le dépôt racine contient `vercel.json` configuré pour :
  - Installer les dépendances : `pip install -r backend/requirements.txt`.
  - Collecter les statiques : `cd backend && python manage.py collectstatic --noinput`.
  - Utiliser `@vercel/python` sur `api/index.py` (wrapper WSGI) avec inclusion des dossiers `backend/**` et `frontend/**`.
  - Router `/static/*` vers `frontend/staticfiles` et toutes les autres routes vers Django via `api/index.py`.

## Variables d'environnement à définir sur Vercel
Définissez ces variables dans **Project Settings > Environment Variables** :
- `SECRET_KEY` : clé secrète Django.
- `DJANGO_SETTINGS_MODULE=agcf_voyage.settings`.
- `DJANGO_DEBUG` : `false` en production.
- `ALLOWED_HOSTS` : par ex. `your-project.vercel.app,example.com`.
- `CSRF_TRUSTED_ORIGINS` : par ex. `https://your-project.vercel.app,https://example.com`.
- Base de données : soit `DATABASE_URL`, soit `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Toute autre variable spécifique au projet (API keys, email…).

## Préparer la base de données
1. Créez la base sur votre fournisseur (MySQL, Postgres, etc.).
2. Configurez `DATABASE_URL` ou les variables MySQL correspondantes dans Vercel.
3. Après un premier déploiement, appliquez les migrations :
   ```bash
   vercel env pull .env.local  # optionnel pour synchroniser les variables en local
   cd backend
   python manage.py migrate
   ```
   Avec une base gérée à distance (Railway, Render, ElephantSQL…), exécutez `python manage.py migrate` en pointant vers cette base (via `DATABASE_URL`).

## Déploiement à partir de GitHub
1. Poussez le dépôt sur GitHub.
2. Sur le tableau de bord Vercel, **New Project** > **Import Git Repository** et sélectionnez le dépôt.
3. Dans la configuration d'import :
   - Racine du projet : `/` (car `vercel.json` est au root).
   - Commande d'installation : laissée par `vercel.json` (`pip install -r backend/requirements.txt`).
   - Build command : définie dans `vercel.json`.
   - Output : laissé vide (Vercel utilisera les lambdas Python).
4. Ajoutez les variables d'environnement.
5. Lancez le déploiement. Chaque `git push` vers la branche configurée déclenchera un déploiement automatique.

## Domaine personnalisé
1. Dans Vercel, ouvrez votre projet > **Settings** > **Domains** > **Add** et saisissez votre domaine.
2. Configurez vos DNS chez le registrar :
   - CNAME `www` vers `cname.vercel-dns.com` (ou valeur fournie).
   - Optionnel : enregistrement A ou ALIAS/ANAME pour le domaine racine selon les instructions Vercel.
3. Une fois la propagation DNS terminée, ajoutez le domaine à `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` puis redéployez si nécessaire.

## Vérifications post-déploiement
- `/static/*` renvoie les assets collectés (fichiers générés dans `frontend/staticfiles`).
- L'application se charge sans erreurs 500 et les formulaires ne déclenchent pas d'avertissements CSRF.
- Les URL de rappel (emails, QR codes) utilisent le domaine public.
