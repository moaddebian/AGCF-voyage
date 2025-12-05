# 🔧 CORRECTION ERREUR RAILWAY - Python Installation

## Problème
```
ERROR failed to install core:python@3.11.0
ERROR no precompiled python found for core:python@3.11.0
```

## Solution appliquée

### 1. Modification de `runtime.txt`
- **Avant** : `python-3.11.0` (version trop spécifique)
- **Après** : `python-3.11.9` (version plus récente et disponible)

### 2. Modification de `nixpacks.toml`
- Ajout de `pip install --upgrade pip` pour s'assurer que pip est à jour
- Utilisation de `python311` dans nixPkgs

## Alternative : Supprimer runtime.txt

Si le problème persiste, vous pouvez **supprimer complètement** `runtime.txt`. Railway détectera automatiquement la version Python depuis vos dépendances.

```bash
# Supprimer runtime.txt
rm runtime.txt
```

Railway utilisera alors la version Python par défaut (généralement 3.11 ou 3.12).

## Variables d'environnement à configurer sur Railway

⚠️ **IMPORTANT** : Ne jamais hardcoder les clés API dans le code ! Utilisez les variables d'environnement sur Railway :

### Cloudinary
```
CLOUDINARY_CLOUD_NAME=df0c3lvlx
CLOUDINARY_API_KEY=771282459579441
CLOUDINARY_API_SECRET=psW0mqjrl97hSXeYAt-YgSziVFQ
```

### Resend
```
RESEND_API_KEY=re_BBvNeWKM_5Bt8njhGeFQcTYdEt3pbUVpV
EMAIL_FROM=agcf-voyage@agcf.com
```

### Django
```
SECRET_KEY=<générer-une-clé-secrète>
DJANGO_DEBUG=False
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
CSRF_TRUSTED_ORIGINS=https://votre-app.railway.app
```

### Base de données
```
DATABASE_URL=<automatiquement ajouté par Railway PostgreSQL>
```

## Étapes suivantes

1. **Commit et push** les modifications :
```bash
git add .
git commit -m "Fix Railway Python version and environment variables"
git push
```

2. **Sur Railway** :
   - Allez dans votre projet
   - Cliquez sur "Variables" dans votre service Django
   - Ajoutez toutes les variables d'environnement ci-dessus
   - Redéployez

3. **Vérifier les logs** :
   - Si l'erreur persiste, vérifiez les logs Railway
   - L'erreur devrait maintenant être résolue

## Si le problème persiste

1. **Supprimer `runtime.txt`** complètement
2. **Supprimer `nixpacks.toml`** et laisser Railway détecter automatiquement
3. Railway utilisera alors sa configuration par défaut

