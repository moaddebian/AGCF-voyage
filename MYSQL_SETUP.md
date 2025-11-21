# Configuration MySQL pour AGCF Voyages

Ce guide vous explique comment connecter votre projet Django à une base de données MySQL.

## Prérequis

1. **MySQL installé sur votre système**
   - Télécharger depuis : https://dev.mysql.com/downloads/mysql/
   - Ou utiliser XAMPP/WAMP qui inclut MySQL

2. **Créer une base de données MySQL**

## Étapes d'installation

### 1. Installer MySQL sur votre système

#### Windows
- Téléchargez MySQL Installer depuis le site officiel
- Ou utilisez XAMPP/WAMP qui inclut MySQL

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

#### macOS
```bash
brew install mysql
brew services start mysql
```

### 2. Créer la base de données MySQL

Connectez-vous à MySQL :
```bash
mysql -u root -p
```

Créez la base de données :
```sql
CREATE DATABASE agcf_voyage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agcf_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON agcf_voyage.* TO 'agcf_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Installer le driver MySQL pour Python

#### Option 1 : mysqlclient (recommandé)
```bash
pip install mysqlclient
```

**Note pour Windows :** Si l'installation échoue, téléchargez le wheel précompilé depuis :
https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

Ou installez les outils de compilation :
- Téléchargez Visual C++ Build Tools
- Installez MySQL Connector/C

#### Option 2 : PyMySQL (alternative plus facile)
Si `mysqlclient` ne s'installe pas, utilisez `PyMySQL` :

1. Installez PyMySQL :
```bash
pip install PyMySQL
```

2. Ajoutez ce code au début de `agcf_voyage/__init__.py` :
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 4. Configurer les paramètres de connexion

#### Méthode 1 : Variables d'environnement (recommandé)

Créez un fichier `.env` à la racine du projet :
```env
DB_NAME=agcf_voyage
DB_USER=agcf_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306
```

Installez python-decouple :
```bash
pip install python-decouple
```

Modifiez `agcf_voyage/settings.py` :
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='agcf_voyage'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

#### Méthode 2 : Configuration directe

Modifiez directement `agcf_voyage/settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'agcf_voyage',
        'USER': 'agcf_user',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### 5. Effectuer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Initialiser les données de test

```bash
python manage.py init_data
```

## Vérification de la connexion

Testez la connexion :
```bash
python manage.py dbshell
```

Si vous voyez l'invite MySQL, la connexion fonctionne !

## Dépannage

### Erreur : "No module named 'MySQLdb'"
- Installez `mysqlclient` ou utilisez `PyMySQL` (voir Option 2 ci-dessus)

### Erreur : "Access denied for user"
- Vérifiez le nom d'utilisateur et le mot de passe
- Vérifiez que l'utilisateur a les permissions sur la base de données

### Erreur : "Can't connect to MySQL server"
- Vérifiez que MySQL est démarré :
  - Windows : Services → MySQL
  - Linux : `sudo systemctl status mysql`
  - macOS : `brew services list`
- Vérifiez que le port 3306 est correct

### Erreur : "Unknown database"
- Créez la base de données (voir étape 2)

### Erreur lors de l'installation de mysqlclient sur Windows
1. Téléchargez le wheel précompilé depuis https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
2. Installez-le avec : `pip install mysqlclient‑2.2.0‑cp39‑cp39‑win_amd64.whl` (adaptez la version)
3. Ou utilisez PyMySQL à la place

## Retour à SQLite

Si vous voulez revenir à SQLite, modifiez `settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Sécurité

⚠️ **Important pour la production :**
- Ne commitez jamais les mots de passe dans le code
- Utilisez des variables d'environnement
- Utilisez un utilisateur MySQL avec des permissions limitées
- Activez SSL pour les connexions MySQL en production

---

**Configuration terminée ! Votre projet est maintenant connecté à MySQL.** 🎉

