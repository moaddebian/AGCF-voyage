# Variables d'environnement Vercel

## Variables obligatoires

Configurez ces variables dans votre projet Vercel (Settings > Environment Variables) :

### 1. SECRET_KEY (OBLIGATOIRE)
```
SECRET_KEY=votre-secret-key-django-tres-securise-et-longue
```
**Important** : Générez une nouvelle clé secrète pour la production :
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. DEBUG
```
DEBUG=False
```
Mettez `False` en production pour la sécurité.

### 3. ALLOWED_HOSTS
```
ALLOWED_HOSTS=agcf-voyagema.vercel.app,*.vercel.app
```
Remplacez `agcf-voyagema.vercel.app` par votre domaine Vercel.

## Variables de base de données MySQL (optionnel)

Si vous utilisez MySQL, configurez ces variables :

```
DB_NAME=agcf_voyage
DB_USER=votre_utilisateur_mysql
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=votre_host_mysql
DB_PORT=3306
```

**Note** : Si ces variables ne sont pas définies, l'application utilisera SQLite par défaut (limité sur Vercel car pas de persistance).

## Variables email (optionnel)

Pour l'envoi d'emails réels :

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
```

## Comment configurer dans Vercel

1. Allez sur https://vercel.com
2. Sélectionnez votre projet
3. Allez dans **Settings** > **Environment Variables**
4. Ajoutez chaque variable pour **Production**, **Preview**, et **Development**
5. Cliquez sur **Save**
6. Redéployez votre application

## Vérification

Après avoir configuré les variables, vérifiez dans les logs Vercel que l'application démarre correctement.

