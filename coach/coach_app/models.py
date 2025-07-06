from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_coach = models.BooleanField(default=False, verbose_name="Est un coach")
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"Profil de {self.user.username} ({'Coach' if self.is_coach else 'Client'})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Exercice(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    duree = models.CharField(max_length=50, help_text="ex: 60 minutes")
    tarif = models.DecimalField(max_digits=6, decimal_places=2)
    details = models.TextField(blank=True, help_text="Détails supplémentaires")
    
    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
    
    def __str__(self):
        return f"{self.nom} - {self.tarif}€"

class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('termine', 'Terminé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rendez_vous')
    session = models.ForeignKey('SessionReservation', on_delete=models.CASCADE, related_name='rendez_vous', null=True, blank=True)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='rendez_vous', null=True, blank=True)
    date = models.DateField()
    heure = models.CharField(max_length=5, help_text="Format: HH:MM")
    duree = models.CharField(max_length=50, blank=True, help_text="Durée de l'exercice au moment du RDV")
    tarif = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Tarif de l'exercice au moment du RDV")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    notes_personnelles = models.TextField(blank=True, verbose_name="Notes personnelles (coach uniquement)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"

    def __str__(self):
        return f"RDV {self.user.username} - {self.date} à {self.heure}"

    def clean(self):
        if self.date and self.heure:
            conflits = RendezVous.objects.filter(
                date=self.date,
                heure=self.heure
            ).exclude(pk=self.pk)
            
            if conflits.exists():
                raise ValidationError(
                    f"Ce créneau ({self.date} à {self.heure}) est déjà réservé."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class NoteHistorique(models.Model):
    """Historique des notes du coach pour un rendez-vous"""
    rendez_vous = models.ForeignKey(RendezVous, on_delete=models.CASCADE, related_name='notes_historique')
    contenu = models.TextField(verbose_name="Contenu de la note")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Note historique"
        verbose_name_plural = "Notes historiques"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Note du {self.date_creation.strftime('%d/%m/%Y %H:%M')} - {self.rendez_vous.user.username}"

class SessionReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_reservation')
    total_tarif = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Session de réservation"
        verbose_name_plural = "Sessions de réservation"
    
    def __str__(self):
        return f"Session {self.user.username} - {self.total_tarif}€ - {self.created_at.strftime('%d/%m/%Y')}"
    
    def calculer_total(self):
        # Ne calculer que les RDV en attente (non traités par le coach)
        total = sum(rdv.tarif for rdv in self.rendez_vous.filter(statut='en_attente') if rdv.tarif)
        self.total_tarif = total
        self.save()
        return total

class RDVTemporaire(models.Model):
    """Rendez-vous temporaire avant validation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rdv_temporaires')
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='rdv_temporaires')
    date = models.DateField()
    heure = models.CharField(max_length=5, help_text="Format: HH:MM")
    duree = models.CharField(max_length=50, blank=True)
    tarif = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rdv_origine = models.ForeignKey('RendezVous', null=True, blank=True, on_delete=models.SET_NULL, related_name='modifications_temp')
    
    class Meta:
        verbose_name = "Rendez-vous temporaire"
        verbose_name_plural = "Rendez-vous temporaires"
        unique_together = ['user', 'date', 'heure']  # Un seul RDV temporaire par créneau
    
    def __str__(self):
        return f"RDV temp {self.user.username} - {self.date} à {self.heure}"
    
    def clean(self):
        if self.date and self.heure:
            # Vérifier les conflits avec les RDV temporaires
            conflits_temp = RDVTemporaire.objects.filter(
                date=self.date,
                heure=self.heure
            ).exclude(pk=self.pk)
            
            # Vérifier les conflits avec les RDV définitifs
            conflits_def = RendezVous.objects.filter(
                date=self.date,
                heure=self.heure
            )
            
            if conflits_temp.exists() or conflits_def.exists():
                raise ValidationError(
                    f"Ce créneau ({self.date} à {self.heure}) est déjà réservé."
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
