from django.contrib import admin
from .models import RendezVous, Exercice, SessionReservation

@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'duree', 'tarif')
    list_filter = ('tarif',)
    search_fields = ('nom', 'description')
    ordering = ('nom',)

@admin.register(SessionReservation)
class SessionReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_tarif', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'exercice', 'date', 'heure', 'tarif', 'created_at')
    list_filter = ('date', 'heure', 'exercice', 'session', 'created_at')
    search_fields = ('user__username', 'user__email', 'exercice__nom')
    date_hierarchy = 'date'
    ordering = ('-date', '-heure')
