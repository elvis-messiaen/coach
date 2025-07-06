from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rendez_vous')
    session = models.ForeignKey('SessionReservation', on_delete=models.CASCADE, related_name='rendez_vous', null=True, blank=True)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='rendez_vous', null=True, blank=True)
    date = models.DateField()
    heure = models.CharField(max_length=5, help_text="Format: HH:MM")
    duree = models.CharField(max_length=50, blank=True, help_text="Durée de l'exercice au moment du RDV")
    tarif = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Tarif de l'exercice au moment du RDV")
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
        total = sum(rdv.tarif for rdv in self.rendez_vous.all() if rdv.tarif)
        self.total_tarif = total
        self.save()
        return total
