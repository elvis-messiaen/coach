#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coach.settings')
django.setup()

from django.contrib.auth.models import User
from coach_app.models import RendezVous, Exercice, SessionReservation

def create_test_rdv():
    """Créer des rendez-vous de test pour tester le système coach"""
    
    # Récupérer les utilisateurs
    try:
        client1 = User.objects.get(username='louis')
        client2 = User.objects.get(username='paul')
        client3 = User.objects.get(username='pil')
    except User.DoesNotExist as e:
        print(f"Utilisateur non trouvé: {e}")
        return
    
    # Récupérer les exercices
    exercices = Exercice.objects.all()
    if not exercices.exists():
        print("Aucun exercice trouvé. Créez d'abord des exercices.")
        return
    
    # Dates de test
    today = date.today()
    dates_test = [
        today + timedelta(days=1),  # Demain
        today + timedelta(days=2),  # Après-demain
        today + timedelta(days=-1), # Hier (terminé)
        today + timedelta(days=-2), # Avant-hier (terminé)
    ]
    
    heures_test = ['09:00', '10:00', '14:00', '15:00']
    
    rdv_crees = 0
    
    for i, client in enumerate([client1, client2, client3]):
        exercice = exercices[i % len(exercices)]
        
        for j, date_rdv in enumerate(dates_test):
            heure = heures_test[j % len(heures_test)]
            
            # Créer une session de réservation
            session, created = SessionReservation.objects.get_or_create(
                user=client,
                defaults={'total_tarif': 0}
            )
            
            # Déterminer le statut selon la date
            if date_rdv < today:
                statut = 'termine'
            elif j == 0:
                statut = 'en_attente'
            else:
                statut = 'valide'
            
            # Créer le rendez-vous
            rdv, created = RendezVous.objects.get_or_create(
                user=client,
                date=date_rdv,
                heure=heure,
                exercice=exercice,
                defaults={
                    'session': session,
                    'duree': exercice.duree,
                    'tarif': exercice.tarif,
                    'statut': statut,
                    'notes_personnelles': f"Note de test pour {client.username} - {exercice.nom}"
                }
            )
            
            if created:
                rdv_crees += 1
                print(f"RDV créé: {client.username} - {exercice.nom} - {date_rdv} à {heure} - {statut}")
            
            # Mettre à jour le total de la session
            session.calculer_total()
    
    print(f"\n🎉 {rdv_crees} rendez-vous de test créés avec succès!")
    print("\nVous pouvez maintenant tester le système coach en vous connectant avec 'elvis'")

if __name__ == "__main__":
    create_test_rdv() 