from datetime import date, datetime, timedelta
import calendar
import locale
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import RendezVous, Exercice, SessionReservation

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

def home(request):
    return render(request, 'coach_app/base.html')

def a_propos(request):
    return render(request, 'coach_app/a_propos.html')

def accueil(request):
    return render(request, 'coach_app/accueil.html')

def contact(request):
    if request.method == 'POST':
        sujet = request.POST.get('sujet')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if sujet and nom and email and message:
            try:
                email_content = f"""
Nouveau message de contact reçu :

Sujet : {sujet}
Nom : {nom}
Email : {email}

Message :
{message}

---
Ce message a été envoyé depuis le formulaire de contact du site Coach App.
                """
                
                messages.success(request, "Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.")
                return redirect('coach:contact')
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi du message : {str(e)}")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire.")
    
    return render(request, 'coach_app/contact.html')

@login_required
def rendez_vous(request):
    mois_param = request.GET.get("mois")
    annee_param = request.GET.get("annee")
    exercice_id = request.GET.get("exercice")
    date_selectionnee = request.GET.get("date")
    heure_modification = request.GET.get("heure")
    mode_modification = request.GET.get("modifier") == "true"

    today = date.today()
    
    month = int(mois_param) if mois_param else today.month
    year = int(annee_param) if annee_param else today.year

    displayed_date = date(year, month, 1)
    nom_mois = displayed_date.strftime("%B").capitalize()

    _, last_day = calendar.monthrange(year, month)
    prev_month_date = displayed_date - timedelta(days=1)
    next_month_date = displayed_date + timedelta(days=last_day)

    mois_precedent = {
        "mois": prev_month_date.month,
        "annee": prev_month_date.year,
        "nom": prev_month_date.strftime("%B").capitalize()
    }
    mois_suivant = {
        "mois": next_month_date.month,
        "annee": next_month_date.year,
        "nom": next_month_date.strftime("%B").capitalize()
    }

    jours_du_mois = []
    for day in range(1, last_day + 1):
        jour_date = date(year, month, day)
        jours_du_mois.append({
            "numero": day,
            "date": jour_date,
            "disable": jour_date < today
        })

    premier_jour = displayed_date.weekday()
    range_precalé = range(premier_jour)
    jours_semaine = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

    now = datetime.now()
    heure_actuelle = now.hour
    
    heures_disponibles = []
    current_time = datetime.strptime("07:00", "%H:%M")
    end_time = datetime.strptime("22:00", "%H:%M")
    
    while current_time < end_time:
        heures_disponibles.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=40)

    exercices = Exercice.objects.all().order_by('nom')
    exercice_selectionne = None
    
    if mode_modification and not exercice_id and 'modification_rdv' in request.session:
        modif_data = request.session['modification_rdv']
        exercice_id = modif_data['exercice_id']
    
    if exercice_id:
        try:
            exercice_selectionne = Exercice.objects.get(id=exercice_id)
        except Exercice.DoesNotExist:
            exercice_selectionne = None

    creneaux_reserves = []
    if date_selectionnee:
        try:
            date_obj = datetime.strptime(date_selectionnee, "%Y-%m-%d").date()
            creneaux_reserves = list(RendezVous.objects.filter(
                date=date_obj
            ).values_list('heure', flat=True))
        except:
            pass
    
    rdv_en_modification = None
    if mode_modification and 'modification_rdv' in request.session:
        modif_data = request.session['modification_rdv']
        if modif_data['date'] == date_selectionnee:
            if modif_data['heure'] in creneaux_reserves:
                creneaux_reserves.remove(modif_data['heure'])
            rdv_en_modification = modif_data

    context = {
        "mois_actuel": f"{nom_mois} {year}",
        "mois_precedent": mois_precedent,
        "mois_suivant": mois_suivant,
        "jours_semaine": jours_semaine,
        "range_precalé": range_precalé,
        "jours_du_mois": jours_du_mois,
        "date_selectionnee": date_selectionnee,
        "heure_limite": heure_actuelle + 1 if date_selectionnee == today.strftime("%Y-%m-%d") else 0,
        "heures_disponibles": heures_disponibles,
        "creneaux_reserves": creneaux_reserves,
        "today": today,
        "month": month,
        "year": year,
        "exercices": exercices,
        "exercice_selectionne": exercice_selectionne,
        "mode_modification": mode_modification,
        "heure_modification": heure_modification,
        "rdv_en_modification": rdv_en_modification,
    }

    return render(request, "coach_app/prise_rdv.html", context)

@login_required
def ajouter_creneau(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        exercice_id = data.get('exercice_id')
        date_str = data.get('date')
        heure = data.get('heure')
        
        try:
            exercice = Exercice.objects.get(id=exercice_id)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            modification_en_cours = 'modification_rdv' in request.session
            
            conflit = None
            if modification_en_cours:
                modif_data = request.session['modification_rdv']
                conflit = RendezVous.objects.filter(
                    date=date_obj,
                    heure=heure
                ).exclude(id=modif_data['rdv_id']).first()
            else:
                conflit = RendezVous.objects.filter(
                    date=date_obj,
                    heure=heure
                ).first()
            
            if conflit:
                return JsonResponse({
                    'success': False,
                    'message': f'Ce créneau est déjà réservé pour {conflit.exercice.nom}'
                })
            
            if modification_en_cours:
                modif_data = request.session['modification_rdv']
                try:
                    ancien_rdv = RendezVous.objects.get(id=modif_data['rdv_id'], user=request.user)
                    session = ancien_rdv.session
                    ancien_rdv.delete()
                    del request.session['modification_rdv']
                except RendezVous.DoesNotExist:
                    session = None
            
            if not modification_en_cours or not session:
                session, created = SessionReservation.objects.get_or_create(
                    user=request.user,
                    defaults={'total_tarif': 0}
                )
            
            rdv = RendezVous.objects.create(
                user=request.user,
                session=session,
                exercice=exercice,
                date=date_obj,
                heure=heure,
                duree=exercice.duree,
                tarif=exercice.tarif
            )
            
            session.calculer_total()
            
            message = f'Créneau modifié : {exercice.nom} le {date_str} à {heure}h00' if modification_en_cours else f'Créneau ajouté : {exercice.nom} le {date_str} à {heure}h00'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'total': float(session.total_tarif),
                'rdv_id': rdv.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur : {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def supprimer_creneau(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        rdv_id = data.get('rdv_id')
        
        try:
            rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
            session = rdv.session
            rdv.delete()
            
            if session:
                session.calculer_total()
                total = float(session.total_tarif)
            else:
                total = 0
            
            return JsonResponse({
                'success': True,
                'message': 'Créneau supprimé',
                'total': total
            })
            
        except RendezVous.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Rendez-vous non trouvé'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def valider_reservation(request):
    if request.method == 'POST':
        try:
            session = SessionReservation.objects.filter(user=request.user).order_by('-created_at').first()
            
            if not session or not session.rendez_vous.exists():
                messages.error(request, "Aucune réservation à valider.")
                return redirect('coach:rendez_vous')
            
            messages.success(request, f"Réservation validée ! Total : {session.total_tarif}€")
            return redirect('coach:votre_rendez_vous')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la validation : {str(e)}")
            return redirect('coach:rendez_vous')
    
    return redirect('coach:rendez_vous')

@login_required
def votre_rendez_vous(request):
    sessions = SessionReservation.objects.filter(user=request.user).order_by('-created_at')
    
    if sessions.exists():
        session_actuelle = sessions.first()
        rendez_vous_list = session_actuelle.rendez_vous.all().order_by('date', 'heure')
        
        rdv_formatted = []
        for rdv in rendez_vous_list:
            import locale
            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_TIME, 'fr_FR')
                except:
                    pass
            
            jour_formaté = rdv.date.strftime("%d %B %Y")
            heure_formatée = rdv.heure
            
            rdv_formatted.append({
                "id": rdv.id,
                "jour": jour_formaté,
                "heure": heure_formatée,
                "exercice": rdv.exercice.nom if rdv.exercice else "Non spécifié",
                "duree": rdv.duree,
                "tarif": rdv.tarif
            })
        
        return render(request, 'coach_app/dashboard.html', {
            "session_actuelle": session_actuelle,
            "rendez_vous_list": rdv_formatted,
            "total_tarif": session_actuelle.total_tarif
        })
    else:
        return render(request, 'coach_app/dashboard.html', {
            "message": "Aucun rendez-vous n'est encore enregistré."
        })

@login_required
def supprimer_rendez_vous(request, rdv_id):
    if request.method == 'POST':
        try:
            rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
            session = rdv.session
            rdv.delete()
            
            if session and session.rendez_vous.exists():
                session.calculer_total()
                messages.success(request, "Rendez-vous supprimé avec succès.")
            else:
                if session:
                    session.delete()
                messages.success(request, "Rendez-vous supprimé. Session fermée.")
            
            return redirect('coach:votre_rendez_vous')
            
        except RendezVous.DoesNotExist:
            messages.error(request, "Rendez-vous non trouvé.")
            return redirect('coach:votre_rendez_vous')
    
    return redirect('coach:votre_rendez_vous')

@login_required
def modifier_rendez_vous(request, rdv_id):
    if request.method == 'POST':
        try:
            rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
            
            exercice_id = rdv.exercice.id if rdv.exercice else None
            date_rdv = rdv.date.strftime('%Y-%m-%d')
            heure_rdv = rdv.heure
            
            request.session['modification_rdv'] = {
                'rdv_id': rdv_id,
                'exercice_id': exercice_id,
                'date': date_rdv,
                'heure': heure_rdv
            }
            
            redirect_url = f"{reverse('coach:rendez_vous')}?exercice={exercice_id}&modifier=true"
            messages.success(request, f"Modification en cours. Choisissez un nouveau créneau pour remplacer l'ancien.")
            return redirect(redirect_url)
            
        except RendezVous.DoesNotExist:
            messages.error(request, "Rendez-vous non trouvé.")
            return redirect('coach:votre_rendez_vous')
    
    return redirect('coach:votre_rendez_vous')

@login_required
def supprimer_tous_rendez_vous(request):
    if request.method == 'POST':
        try:
            rdv_count = RendezVous.objects.filter(user=request.user).count()
            RendezVous.objects.filter(user=request.user).delete()
            
            SessionReservation.objects.filter(user=request.user).delete()
            
            messages.success(request, f"{rdv_count} rendez-vous supprimés avec succès.")
            return redirect('coach:votre_rendez_vous')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
            return redirect('coach:votre_rendez_vous')
    
    return redirect('coach:votre_rendez_vous')

