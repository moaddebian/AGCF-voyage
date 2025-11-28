"""
Script pour créer un superutilisateur Django de manière non-interactive
"""
import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Informations du superutilisateur
username = input("Nom d'utilisateur: ")
email = input("Email: ")

# Vérifier si l'utilisateur existe déjà
if User.objects.filter(username=username).exists():
    print(f"L'utilisateur '{username}' existe déjà.")
    response = input("Voulez-vous changer le mot de passe? (o/n): ")
    if response.lower() == 'o':
        user = User.objects.get(username=username)
        password = input("Nouveau mot de passe: ")
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Mot de passe mis à jour pour '{username}'.")
    else:
        print("Opération annulée.")
else:
    password = input("Mot de passe: ")
    password_confirm = input("Confirmer le mot de passe: ")
    
    if password != password_confirm:
        print("Les mots de passe ne correspondent pas. Opération annulée.")
    else:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superutilisateur '{username}' créé avec succès!")

