from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Profile, Exercice, RendezVous, RDVTemporaire, NoteHistorique, SessionReservation


class ProfileService:
    """Service pour la gestion des profils utilisateurs"""
    
    @staticmethod
    def get_or_create_profile(user):
        """Récupère ou crée un profil pour un utilisateur"""
        profile, created = Profile.objects.get_or_create(user=user)
        return profile, created
    
    @staticmethod
    def is_coach(user):
        """Vérifie si un utilisateur est un coach"""
        try:
            return user.profile.is_coach
        except Profile.DoesNotExist:
            return False


class AppointmentService:
    """Service pour la gestion des rendez-vous"""
    
    @staticmethod
    def create_temporary_appointment(user, exercice, date, heure):
        """Crée un rendez-vous temporaire"""
        rdv_temp = RDVTemporaire.objects.create(
            user=user,
            exercice=exercice,
            date=date,
            heure=heure,
            duree=exercice.duree,
            tarif=exercice.tarif
        )
        return rdv_temp
    
    @staticmethod
    def create_definitive_appointment(user, exercice, date, heure, duree=60, tarif=50):
        """Crée un rendez-vous définitif"""
        rdv = RendezVous.objects.create(
            user=user,
            exercice=exercice,
            date=date,
            heure=heure,
            duree=duree,
            tarif=tarif
        )
        return rdv
    
    @staticmethod
    def update_appointment(rdv_id, exercice, date, heure, duree=60, tarif=50):
        """Met à jour un rendez-vous existant"""
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        rdv.exercice = exercice
        rdv.date = date
        rdv.heure = heure
        rdv.duree = duree
        rdv.tarif = tarif
        rdv.save()
        return rdv
    
    @staticmethod
    def delete_appointment(rdv_id):
        """Supprime un rendez-vous"""
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        rdv.delete()
    
    @staticmethod
    def delete_temporary_appointment(rdv_temp_id):
        """Supprime un rendez-vous temporaire"""
        rdv_temp = get_object_or_404(RDVTemporaire, id=rdv_temp_id)
        rdv_temp.delete()
    
    @staticmethod
    def get_user_appointments(user):
        """Récupère tous les rendez-vous d'un utilisateur"""
        return RendezVous.objects.filter(user=user).order_by('date', 'heure')
    
    @staticmethod
    def get_user_temporary_appointments(user):
        """Récupère tous les rendez-vous temporaires d'un utilisateur"""
        return RDVTemporaire.objects.filter(user=user).order_by('date', 'heure')
    
    @staticmethod
    def get_pending_appointments():
        """Récupère tous les rendez-vous en attente de validation"""
        return RendezVous.objects.filter(statut='en_attente').order_by('date', 'heure')
    
    @staticmethod
    def get_appointment_history(user):
        """Récupère l'historique des rendez-vous (acceptés/refusés)"""
        return RendezVous.objects.filter(
            user=user,
            statut__in=['valide', 'refuse', 'termine']
        ).order_by('-date', '-heure')


class CoachService:
    """Service pour les fonctionnalités spécifiques aux coaches"""
    
    @staticmethod
    def get_coach_clients():
        """Récupère tous les clients (utilisateurs non-coaches)"""
        return User.objects.filter(profile__is_coach=False)
    
    @staticmethod
    def get_client_appointments(client):
        """Récupère tous les rendez-vous d'un client spécifique"""
        return RendezVous.objects.filter(user=client).order_by('-date', '-heure')
    
    @staticmethod
    def validate_appointment(rdv_id, statut, note_privee=None):
        """Valide ou refuse un rendez-vous"""
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        rdv.statut = statut
        rdv.save()
        
        if note_privee:
            NoteHistorique.objects.create(
                rendez_vous=rdv,
                contenu=note_privee
            )
        
        return rdv
    
    @staticmethod
    def add_private_note(rdv_id, note):
        """Ajoute une note privée à un rendez-vous"""
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        NoteHistorique.objects.create(
            rendez_vous=rdv,
            contenu=note
        )
        return rdv


class ExerciseService:
    """Service pour la gestion des exercices"""
    
    @staticmethod
    def get_all_exercises():
        """Récupère tous les exercices"""
        return Exercice.objects.all().order_by('nom')
    
    @staticmethod
    def get_exercise_by_id(exercise_id):
        """Récupère un exercice par son ID"""
        try:
            return Exercice.objects.get(id=exercise_id)
        except Exercice.DoesNotExist:
            return None


class StatisticsService:
    """Service pour les statistiques"""
    
    @staticmethod
    def get_user_statistics(user):
        """Calcule les statistiques d'un utilisateur"""
        appointments = RendezVous.objects.filter(user=user)
        
        stats = {
            'total_appointments': appointments.count(),
            'pending_appointments': appointments.filter(statut='en_attente').count(),
            'accepted_appointments': appointments.filter(statut='valide').count(),
            'refused_appointments': appointments.filter(statut='refuse').count(),
        }
        
        return stats
    
    @staticmethod
    def get_coach_statistics():
        """Calcule les statistiques pour les coaches"""
        total_appointments = RendezVous.objects.count()
        pending_appointments = RendezVous.objects.filter(statut='en_attente').count()
        total_clients = User.objects.filter(profile__is_coach=False).count()
        
        stats = {
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'total_clients': total_clients,
        }
        
        return stats


class SessionService:
    """Service pour la gestion des sessions de réservation"""
    
    @staticmethod
    def get_or_create_session(user):
        """Récupère ou crée une session de réservation pour un utilisateur"""
        session, created = SessionReservation.objects.get_or_create(
            user=user,
            defaults={'total_tarif': 0}
        )
        return session, created
    
    @staticmethod
    def validate_temporary_appointments(user):
        """Valide tous les rendez-vous temporaires d'un utilisateur"""
        rdv_temporaires = RDVTemporaire.objects.filter(user=user)
        if not rdv_temporaires.exists():
            return None, "Aucune réservation temporaire à valider."
        
        session, created = SessionService.get_or_create_session(user)
        total_tarif = 0
        
        for rdv_temp in rdv_temporaires:
            rdv = RendezVous.objects.create(
                user=user,
                session=session,
                exercice=rdv_temp.exercice,
                date=rdv_temp.date,
                heure=rdv_temp.heure,
                duree=rdv_temp.duree,
                tarif=rdv_temp.tarif,
                statut='en_attente'
            )
            total_tarif += float(rdv_temp.tarif) if rdv_temp.tarif else 0
            rdv_temp.delete()
        
        session.total_tarif = total_tarif
        session.save()
        
        return session, f"Réservation validée ! {rdv_temporaires.count()} créneau(x) ajouté(s). Total : {total_tarif}€"
    
    @staticmethod
    def clear_temporary_appointments(user):
        """Supprime tous les rendez-vous temporaires d'un utilisateur"""
        count = RDVTemporaire.objects.filter(user=user).count()
        RDVTemporaire.objects.filter(user=user).delete()
        return count


class ConflictService:
    """Service pour la gestion des conflits de créneaux"""
    
    @staticmethod
    def check_definitive_conflicts(date, heure, exclude_user=None, exclude_rdv_id=None):
        """Vérifie les conflits avec les rendez-vous définitifs"""
        query = RendezVous.objects.filter(date=date, heure=heure)
        
        if exclude_user:
            query = query.exclude(user=exclude_user)
        
        if exclude_rdv_id:
            query = query.exclude(id=exclude_rdv_id)
        
        return query.first()
    
    @staticmethod
    def check_temporary_conflicts(date, heure, exclude_user=None):
        """Vérifie les conflits avec les rendez-vous temporaires"""
        query = RDVTemporaire.objects.filter(date=date, heure=heure)
        
        if exclude_user:
            query = query.exclude(user=exclude_user)
        
        return query.first()
    
    @staticmethod
    def check_all_conflicts(date, heure, exclude_user=None, exclude_rdv_id=None):
        """Vérifie tous les types de conflits"""
        definitive_conflict = ConflictService.check_definitive_conflicts(date, heure, exclude_user, exclude_rdv_id)
        temporary_conflict = ConflictService.check_temporary_conflicts(date, heure, exclude_user)
        
        return definitive_conflict, temporary_conflict