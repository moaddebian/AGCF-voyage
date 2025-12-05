# ⚡ SOLUTION RAPIDE - Supprimer nixpacks.toml

## Action immédiate

J'ai supprimé `nixpacks.toml`. Railway va maintenant **auto-détecter Python** depuis `backend/requirements.txt`.

## Pourquoi ça marche ?

Sans `nixpacks.toml`, Railway :
1. Détecte automatiquement `backend/requirements.txt`
2. Reconnaît que c'est un projet Python
3. Installe les dépendances avec pip
4. **N'essaie plus d'exécuter npm**

## Commandes à exécuter

```bash
# Commit la suppression
git add .
git commit -m "Remove nixpacks.toml - let Railway auto-detect Python"
git push
```

## Configuration sur Railway Dashboard

Après le push, allez sur Railway :

1. **Settings** → **Build**
2. **Laissez "Auto-detect" activé**
3. Railway devrait détecter Python automatiquement

Si Railway ne détecte pas automatiquement :

1. **Settings** → **Build**
2. **Désactivez "Auto-detect"**
3. **Configurez manuellement** :
   - **Build Command** : `cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command** : `cd backend && gunicorn agcf_voyage.wsgi:application --bind 0.0.0.0:$PORT --workers 2`

## Fichiers restants

- ✅ `Procfile` - Commande de démarrage
- ✅ `package.json` - Vide, empêche npm
- ✅ `.railwayignore` - Ignore frontend
- ✅ `railway.json` - Configuration Railway (optionnel)

## Vérification

Après le push, vérifiez les logs Railway :
- ✅ "Detected Python project"
- ✅ "Installing dependencies from requirements.txt"
- ❌ Plus d'erreurs `npm: command not found`

