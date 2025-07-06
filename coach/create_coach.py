#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coach.settings')
django.setup()

from django.contrib.auth.models import User
from coach_app.models import Profile

def create_coach(username):
    """Transforme un utilisateur existant en coach"""
    try:
        user = User.objects.get(username=username)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.is_coach = True
        profile.save()
        
        if created:
            print(f"✅ Profil créé et utilisateur '{username}' transformé en coach")
        else:
            print(f"✅ Utilisateur '{username}' transformé en coach")
            
    except User.DoesNotExist:
        print(f"❌ Utilisateur '{username}' non trouvé")
        print("Utilisateurs disponibles:")
        for user in User.objects.all():
            print(f"  - {user.username} ({user.email})")

def list_users():
    """Liste tous les utilisateurs avec leur statut coach"""
    print("👥 Liste des utilisateurs:")
    for user in User.objects.all():
        is_coach = "Coach" if hasattr(user, 'profile') and user.profile.is_coach else "Client"
        print(f"  - {user.username} ({user.email}) - {is_coach}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        create_coach(username)
    else:
        list_users()
        print("\nPour transformer un utilisateur en coach:")
        print("python create_coach.py <username>") 