# ✅ Checklist de Déploiement Vercel

Utilisez cette checklist pour vérifier que tout est prêt avant de déployer.

## 📁 Fichiers Requis

- [x] `vercel.json` - Configuration Vercel
- [x] `api/index.py` - Point d'entrée Django pour Vercel
- [x] `api/__init__.py` - Package Python
- [x] `backend/requirements.txt` - Toutes les dépendances
- [x] `.gitignore` - Exclut les fichiers sensibles

## ⚙️ Configuration

- [x] `settings.py` - Gestion d'erreur pour `dj_database_url`
- [x] `settings.py` - Configuration des fichiers statiques avec WhiteNoise
- [x] `settings.py` - Variables d'environnement pour production
- [x] `vercel.json` - Routes configurées correctement

## 🔐 Variables d'Environnement à Configurer sur Vercel

### Obligatoires :
- [ ] `SECRET_KEY` - Générer une clé secrète Django
- [ ] `DJANGO_SETTINGS_MODULE=agcf_voyage.settings`
- [ ] `DJANGO_DEBUG=false`
- [ ] `ALLOWED_HOSTS` - Votre domaine Vercel (ex: `votre-projet.vercel.app`)
- [ ] `CSRF_TRUSTED_ORIGINS` - Avec https:// (ex: `https://votre-projet.vercel.app`)

### Base de Données (choisir une option) :
- [ ] `DATABASE_URL` - OU
- [ ] `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

### Optionnel (Email) :
- [ ] `EMAIL_HOST`
- [ ] `EMAIL_PORT`
- [ ] `EMAIL_USE_TLS`
- [ ] `EMAIL_HOST_USER`
- [ ] `EMAIL_HOST_PASSWORD`

## 🚀 Étapes Finales

1. [ ] Commiter tous les changements :
   ```bash
   git add .
   git commit -m "Prêt pour déploiement Vercel"
   git push
   ```

2. [ ] Créer le projet sur Vercel et connecter le dépôt GitHub

3. [ ] Configurer toutes les variables d'environnement dans Vercel

4. [ ] Lancer le déploiement

5. [ ] Appliquer les migrations après le premier déploiement :
   ```bash
   vercel env pull .env.local
   cd backend
   python manage.py migrate
   ```

6. [ ] Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

7. [ ] Tester l'application déployée

## ⚠️ Notes de Sécurité

- **NE JAMAIS** commiter de secrets dans le code
- Le mot de passe de la base de données dans `settings.py` ligne 92 est uniquement pour le développement local
- En production sur Vercel, utilisez toujours les variables d'environnement
- Vérifiez que `.env` et `.env.local` sont dans `.gitignore`

## 🔗 Générer une SECRET_KEY

Pour générer une clé secrète Django sécurisée :

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou en ligne de commande :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

