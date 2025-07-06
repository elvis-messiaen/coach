#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coach.settings')
django.setup()

from coach_app.models import Exercice

Exercice.objects.all().delete()
exercices_data = [
    {
        'nom': 'Séance sur mesure',
        'description': 'Renforcement musculaire, cardio et mobilité ciblée selon tes besoins.',
        'duree': '60 minutes',
        'tarif': 60.00,
        'details': 'Suivi personnalisé et plan post-séance'
    },
    {
        'nom': 'Pack transformation 4 semaines',
        'description': 'Résultats visibles dès la 2e semaine avec un plan complet.',
        'duree': '4 séances/semaine',
        'tarif': 220.00,
        'details': 'Bilan initial + plan nutrition, Suivi et ajustement chaque semaine'
    },
    {
        'nom': 'Suivi nutritionnel',
        'description': 'Alimentation adaptée à ton corps, ton rythme et tes objectifs.',
        'duree': 'Consultation + bilan hebdomadaire',
        'tarif': 90.00,
        'details': 'Plan nutrition personnalisé et évolutif'
    },
    {
        'nom': 'Pilates Power',
        'description': 'Inspiré des studios de Miami Beach, pour posture, équilibre et contrôle corporel.',
        'duree': '60 minutes',
        'tarif': 50.00,
        'details': 'Travail du centre (core), Mobilité et tonus global'
    },
    {
        'nom': 'HIIT Performance',
        'description': 'Entraînement haute intensité comme pratiqué par les stars.',
        'duree': '45 minutes',
        'tarif': 70.00,
        'details': 'Circuits explosifs à haute fréquence, Brûle-graisses et gain de puissance'
    },
    {
        'nom': 'Bootcamp plage',
        'description': 'Cardio, renfo et fun, les pieds dans le sable de Miami.',
        'duree': '75 minutes',
        'tarif': 65.00,
        'details': 'Tyres, cordes, medicine balls, Entraînement fonctionnel complet'
    },
    {
        'nom': 'Boxe & Coordination',
        'description': 'Travail de la précision, du cardio et de la posture avec des techniques de boxe.',
        'duree': '60 minutes',
        'tarif': 55.00,
        'details': 'Gants, sac et shadow boxing, Amélioration du rythme et de la réactivité'
    },
    {
        'nom': 'Altitude Training',
        'description': 'Entraînement simulé en haute altitude pour booster ton endurance.',
        'duree': '90 minutes',
        'tarif': 80.00,
        'details': 'Sessions à oxygène réduit, Amélioration cardio-respiratoire'
    },
    {
        'nom': 'Stretch & Recovery',
        'description': 'Séance dédiée à la récupération musculaire et à la mobilité articulaire.',
        'duree': '45 minutes',
        'tarif': 45.00,
        'details': 'Étirements profonds, Massage gun & respiration guidée'
    }
]

for data in exercices_data:
    exercice = Exercice.objects.create(**data) 