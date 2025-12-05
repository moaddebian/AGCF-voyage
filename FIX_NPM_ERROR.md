# 🔧 CORRECTION ERREUR npm: command not found

## Problème
Railway essaie d'exécuter `npm` alors que c'est un projet Django (Python) pur.

## Solution appliquée

### 1. Création de `.railwayignore`
Fichier pour ignorer les dossiers non nécessaires et forcer Railway à se concentrer sur Python.

### 2. Création de `railway.json`
Configuration explicite pour Railway indiquant :
- Builder : NIXPACKS (pour Python)
- Commande de démarrage : Gunicorn

### 3. Mise à jour de `nixpacks.toml`
Ajout de la variable `NIXPACKS_PYTHON_VERSION` pour forcer Python 3.11.

## Pourquoi cette erreur ?

Railway peut parfois :
1. Détecter automatiquement plusieurs types de projets
2. Essayer d'exécuter npm si des fichiers JavaScript sont présents
3. Confondre avec un projet Node.js si certains patterns sont détectés

## Solutions alternatives

### Option 1 : Forcer le builder Python dans Railway Dashboard
1. Allez dans votre projet Railway
2. Cliquez sur votre service Django
3. Allez dans **Settings** → **Build**
4. Sélectionnez **Nixpacks** comme builder
5. Dans **Build Command**, laissez vide (utilisera nixpacks.toml)

### Option 2 : Supprimer nixpacks.toml temporairement
Si le problème persiste, supprimez `nixpacks.toml` et laissez Railway détecter automatiquement Python depuis `requirements.txt` :

```bash
# Sauvegarder d'abord
mv nixpacks.toml nixpacks.toml.backup

# Puis commit et push
git add .
git commit -m "Remove nixpacks.toml to let Railway auto-detect"
git push
```

### Option 3 : Créer un fichier vide package.json
Créer un `package.json` vide peut empêcher Railway d'essayer npm :

```json
{
  "name": "agcf-voyages",
  "version": "1.0.0",
  "description": "Django project - no npm needed",
  "scripts": {}
}
```

Mais cette solution n'est pas recommandée car elle peut créer d'autres problèmes.

## Vérification

Après avoir commit et push :

1. **Vérifiez les logs Railway** :
   - Les logs ne devraient plus mentionner npm
   - Vous devriez voir : "Installing Python packages..."

2. **Vérifiez le build** :
   - Le build devrait utiliser Python uniquement
   - Pas d'erreurs npm

## Prochaines étapes

1. **Commit les fichiers** :
```bash
git add .railwayignore railway.json nixpacks.toml
git commit -m "Fix npm error - force Python-only build"
git push
```

2. **Sur Railway** :
   - Le déploiement devrait redémarrer automatiquement
   - Vérifiez les logs pour confirmer que npm n'est plus appelé

3. **Si l'erreur persiste** :
   - Allez dans Railway Dashboard → Settings → Build
   - Forcez le builder à "Nixpacks"
   - Ou supprimez `nixpacks.toml` et laissez Railway auto-détecter

