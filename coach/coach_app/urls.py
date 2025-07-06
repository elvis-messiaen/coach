from django.urls import path

from . import views

app_name = 'coach'

urlpatterns = [
    path('', views.home, name='home'),
    path('a_propos/', views.a_propos, name='a_propos'),
    path('accueil/', views.accueil, name='accueil'),
    path('contact/', views.contact, name='contact'),
    path('rendez_vous/', views.rendez_vous, name='rendez_vous'),
    path("votre_rendez_vous/", views.votre_rendez_vous, name="votre_rendez_vous"),
    path("dashboard/", views.votre_rendez_vous, name="dashboard"),
    path('ajouter_creneau/', views.ajouter_creneau, name='ajouter_creneau'),
    path('supprimer_creneau/', views.supprimer_creneau, name='supprimer_creneau'),
    path('valider_reservation/', views.valider_reservation, name='valider_reservation'),
    path('vider_reservation/', views.vider_reservation, name='vider_reservation'),
    path('supprimer_rendez_vous/<int:rdv_id>/', views.supprimer_rendez_vous, name='supprimer_rendez_vous'),
    path('modifier_rendez_vous/<int:rdv_id>/', views.modifier_rendez_vous, name='modifier_rendez_vous'),
    path('supprimer_tous_rendez_vous/', views.supprimer_tous_rendez_vous, name='supprimer_tous_rendez_vous'),
    path('historique-rdv/', views.historique_rdv, name='historique_rdv'),
    
    # URLs Coach
    path('coach/dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('coach/historique/', views.coach_historique, name='coach_historique'),
    path('coach/statistiques/', views.coach_statistiques, name='coach_statistiques'),
    path('coach/valider-rdv/<int:rdv_id>/', views.coach_valider_rdv, name='coach_valider_rdv'),
    path('coach/details-rdv/<int:rdv_id>/', views.coach_details_rdv, name='coach_details_rdv'),
]