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
    path('ajouter_creneau/', views.ajouter_creneau, name='ajouter_creneau'),
    path('supprimer_creneau/', views.supprimer_creneau, name='supprimer_creneau'),
    path('valider_reservation/', views.valider_reservation, name='valider_reservation'),
    path('supprimer_rendez_vous/<int:rdv_id>/', views.supprimer_rendez_vous, name='supprimer_rendez_vous'),
    path('modifier_rendez_vous/<int:rdv_id>/', views.modifier_rendez_vous, name='modifier_rendez_vous'),
    path('supprimer_tous_rendez_vous/', views.supprimer_tous_rendez_vous, name='supprimer_tous_rendez_vous'),
]