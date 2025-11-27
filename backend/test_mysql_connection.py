"""
Script de test pour vérifier la connexion MySQL
Usage: python test_mysql_connection.py
"""
import os
import sys

def test_mysql_connection():
    """Teste la connexion à MySQL avec les paramètres du projet"""
    
    # Paramètres de connexion (modifiez selon votre configuration)
    db_config = {
        'NAME': os.environ.get('DB_NAME', 'agcf_voyage'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
    
    print("=" * 50)
    print("Test de connexion MySQL")
    print("=" * 50)
    print(f"Base de données: {db_config['NAME']}")
    print(f"Utilisateur: {db_config['USER']}")
    print(f"Hôte: {db_config['HOST']}")
    print(f"Port: {db_config['PORT']}")
    print("=" * 50)
    
    # Test 1: Vérifier si mysqlclient est installé
    print("\n1. Vérification du driver MySQL...")
    try:
        import MySQLdb
        print("✓ mysqlclient est installé")
        driver = "mysqlclient"
    except ImportError:
        try:
            import pymysql
            pymysql.install_as_MySQLdb()
            import MySQLdb
            print("✓ PyMySQL est installé et configuré")
            driver = "PyMySQL"
        except ImportError:
            print("✗ Aucun driver MySQL trouvé")
            print("  Installez mysqlclient ou PyMySQL:")
            print("  pip install mysqlclient")
            print("  ou")
            print("  pip install PyMySQL")
            return False
    
    # Test 2: Tester la connexion
    print("\n2. Test de connexion à MySQL...")
    try:
        conn = MySQLdb.connect(
            host=db_config['HOST'],
            port=int(db_config['PORT']),
            user=db_config['USER'],
            passwd=db_config['PASSWORD'],
            db=db_config['NAME'],
            charset='utf8mb4'
        )
        print("✓ Connexion réussie !")
        
        # Test 3: Vérifier que la base de données existe
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"✓ Base de données '{db_name}' accessible")
        
        # Test 4: Vérifier le charset
        cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
        charset = cursor.fetchone()
        if charset:
            print(f"✓ Charset: {charset[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✓ Tous les tests sont passés avec succès !")
        print("=" * 50)
        return True
        
    except MySQLdb.Error as e:
        print(f"✗ Erreur de connexion: {e}")
        print("\nVérifiez:")
        print("  - Que MySQL est démarré")
        print("  - Que la base de données existe")
        print("  - Que l'utilisateur a les bonnes permissions")
        print("  - Que le mot de passe est correct")
        return False
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        return False

if __name__ == '__main__':
    success = test_mysql_connection()
    sys.exit(0 if success else 1)

