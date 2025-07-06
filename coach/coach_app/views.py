from datetime import date, datetime, timedelta
import calendar
import locale
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import RendezVous, Exercice, SessionReservation, User, NoteHistorique, RDVTemporaire
from .services import ProfileService, AppointmentService, CoachService, ExerciseService, StatisticsService, SessionService, ConflictService

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
    exercice_id = request.GET.get("exercice") or request.GET.get("exercice_id")
    date_selectionnee = request.GET.get("date")
    heure_modification = request.GET.get("heure")
    mode_modification = request.GET.get("modifier") == "true"
    rdv_id = request.GET.get("rdv_id")

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

    exercices = ExerciseService.get_all_exercises()
    exercice_selectionne = None
    
    if exercice_id:
        exercice_selectionne = ExerciseService.get_exercise_by_id(exercice_id)

    creneaux_reserves = []
    if date_selectionnee:
        try:
            date_obj = datetime.strptime(date_selectionnee, "%Y-%m-%d").date()
            creneaux_reserves = list(RendezVous.objects.filter(
                date=date_obj
            ).values_list('heure', flat=True))
        except:
            pass
    
    # Récupérer les RDV temporaires de l'utilisateur
    rdv_temporaires = AppointmentService.get_user_temporary_appointments(request.user)
    
    # Calculer le total des RDV temporaires
    total_temporaire = sum(float(rdv.tarif or 0) for rdv in rdv_temporaires) if rdv_temporaires else 0

    # Identifier les créneaux déjà sélectionnés par l'utilisateur
    rdv_temp_date = []
    heures_selectionnees = []
    if rdv_temporaires and date_selectionnee:
        try:
            date_obj = datetime.strptime(date_selectionnee, "%Y-%m-%d").date()
            rdv_temp_date = list(rdv_temporaires.filter(date=date_obj))
            heures_selectionnees = [rdv.heure for rdv in rdv_temp_date]
        except:
            pass

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
        "rdv_id": rdv_id,
        "rdv_temporaires": rdv_temporaires,
        "total_temporaire": total_temporaire,
        "rdv_temp_date": rdv_temp_date,
        "heures_selectionnees": heures_selectionnees,
    }

    return render(request, "coach_app/prise_rdv.html", context)

@login_required
def ajouter_creneau(request):
    if request.method == 'POST':
        exercice_id = request.POST.get('exercice_id')
        date_str = request.POST.get('date')
        heure = request.POST.get('heure')
        rdv_id = request.POST.get('rdv_id')  # ID du RDV définitif à modifier (optionnel)
        
        try:
            exercice = ExerciseService.get_exercise_by_id(exercice_id)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Si c'est une modification d'un RDV définitif
            if rdv_id:
                try:
                    # Récupérer le RDV à modifier
                    rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
                    
                    # Vérifier les conflits avec le service
                    conflit_def = ConflictService.check_definitive_conflicts(date_obj, heure, exclude_user=request.user, exclude_rdv_id=rdv_id)
                    
                    if conflit_def:
                        messages.error(request, f'Ce créneau est déjà réservé pour {conflit_def.exercice.nom}')
                        url = reverse('coach:rendez_vous') + f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                        return redirect(url)
                    
                    # Utiliser le service pour mettre à jour le RDV
                    AppointmentService.update_appointment(rdv_id, exercice, date_obj, heure, exercice.duree, exercice.tarif)
                    
                    messages.success(request, f'Rendez-vous modifié : {exercice.nom} le {date_str} à {heure}h00')
                    return redirect('coach:votre_rendez_vous')
                    
                except RendezVous.DoesNotExist:
                    messages.error(request, 'Rendez-vous à modifier non trouvé')
                    url = reverse('coach:rendez_vous') + f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                    return redirect(url)
            
            # Sinon, création d'un nouveau RDV temporaire
            else:
                # Supprimer un éventuel RDV temporaire pour ce créneau
                RDVTemporaire.objects.filter(user=request.user, date=date_obj, heure=heure).delete()
                
                # Vérifier tous les conflits avec le service
                conflit_def, conflit_temp = ConflictService.check_all_conflicts(date_obj, heure, exclude_user=request.user)
                
                if conflit_def:
                    messages.error(request, f'Ce créneau est déjà réservé pour {conflit_def.exercice.nom}')
                    url = reverse('coach:rendez_vous') + f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                    return redirect(url)
                
                if conflit_temp:
                    messages.error(request, f'Ce créneau est déjà réservé temporairement')
                    url = reverse('coach:rendez_vous') + f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                    return redirect(url)
                
                # Utiliser le service pour créer le RDV temporaire
                rdv_temp = AppointmentService.create_temporary_appointment(request.user, exercice, date_obj, heure)
                
                messages.success(request, f'Créneau ajouté temporairement : {exercice.nom} le {date_str} à {heure}h00')
                # Rediriger en conservant l'exercice et la date sélectionnés
                url = reverse('coach:rendez_vous') + f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                return redirect(url)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
            url = reverse('coach:rendez_vous')
            if exercice_id and date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    url += f'?exercice={exercice_id}&date={date_str}&mois={date_obj.month}&annee={date_obj.year}'
                except:
                    pass
            return redirect(url)
    
    return redirect(reverse('coach:rendez_vous'))

@login_required
def supprimer_creneau(request):
    if request.method == 'POST':
        rdv_id = request.POST.get('rdv_id')
        exercice_id = request.POST.get('exercice_id')
        date_str = request.POST.get('date')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        
        try:
            # Essayer de supprimer un RDV temporaire d'abord
            AppointmentService.delete_temporary_appointment(rdv_id)
            messages.success(request, 'Créneau temporaire supprimé')
            
        except:
            # Si ce n'est pas un RDV temporaire, essayer un RDV définitif
            try:
                rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
                session = rdv.session
                AppointmentService.delete_appointment(rdv_id)
                
                if session:
                    session.calculer_total()
                
                messages.success(request, 'Créneau supprimé')
                
            except RendezVous.DoesNotExist:
                messages.error(request, 'Rendez-vous non trouvé')
    
    # Rediriger en conservant les paramètres
    url = reverse('coach:rendez_vous')
    if exercice_id and date_str and mois and annee:
        url += f'?exercice={exercice_id}&date={date_str}&mois={mois}&annee={annee}'
    return redirect(url)

@login_required
def valider_reservation(request):
    if request.method == 'POST':
        try:
            session, message = SessionService.validate_temporary_appointments(request.user)
            if session:
                messages.success(request, message)
                return redirect('coach:votre_rendez_vous')
            else:
                messages.error(request, message)
                return redirect(reverse('coach:rendez_vous'))
        except Exception as e:
            messages.error(request, f"Erreur lors de la validation : {str(e)}")
            return redirect(reverse('coach:rendez_vous'))
    return redirect(reverse('coach:rendez_vous'))

@login_required
def votre_rendez_vous(request):
    # Rediriger les coaches vers leur dashboard
    if hasattr(request.user, 'profile') and request.user.profile.is_coach:
        return redirect('coach:coach_dashboard')
    
    sessions = SessionReservation.objects.filter(user=request.user).order_by('-created_at')
    
    # Récupérer les RDV traités par le coach pour l'historique
    rdvs_traites = AppointmentService.get_appointment_history(request.user)
    
    # Calculer les statistiques
    rdvs_acceptes = rdvs_traites.filter(statut='valide').count()
    rdvs_refuses = rdvs_traites.filter(statut='refuse').count()
    rdvs_termines = rdvs_traites.filter(statut='termine').count()
    
    # Récupérer les RDV temporaires
    rdv_temporaires = AppointmentService.get_user_temporary_appointments(request.user)
    
    # Récupérer les RDV définitifs en attente (seulement s'il y a une session)
    rdv_definitifs_en_attente = []
    if sessions.exists():
        session_actuelle = sessions.first()
        # Ne montrer que les RDV en attente (non traités par le coach)
        rendez_vous_definitifs = session_actuelle.rendez_vous.filter(statut='en_attente').order_by('date', 'heure')
        
        for rdv in rendez_vous_definitifs:
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
            
            rdv_definitifs_en_attente.append({
                "id": rdv.id,
                "jour": jour_formaté,
                "heure": heure_formatée,
                "exercice": rdv.exercice.nom if rdv.exercice else "Non spécifié",
                "duree": rdv.duree,
                "tarif": rdv.tarif,
                "temporaire": False
            })
    
    # Formater les RDV temporaires
    rdv_temporaires_formatted = []
    for rdv_temp in rdv_temporaires:
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR')
            except:
                pass
        
        jour_formaté = rdv_temp.date.strftime("%d %B %Y")
        heure_formatée = rdv_temp.heure
        
        rdv_temporaires_formatted.append({
            "id": rdv_temp.id,
            "jour": jour_formaté,
            "heure": heure_formatée,
            "exercice": rdv_temp.exercice.nom if rdv_temp.exercice else "Non spécifié",
            "duree": rdv_temp.duree,
            "tarif": rdv_temp.tarif,
            "temporaire": True
        })
    
    # Calculer les totaux séparément
    total_temporaire = sum(rdv_temp.tarif for rdv_temp in rdv_temporaires if rdv_temp.tarif)
    total_en_attente = sum(rdv['tarif'] for rdv in rdv_definitifs_en_attente if rdv['tarif'])
    total_global = total_temporaire + total_en_attente
    
    context = {
        "session_actuelle": sessions.first() if sessions.exists() else None,
        "rdv_temporaires": rdv_temporaires_formatted,
        "rdv_definitifs_en_attente": rdv_definitifs_en_attente,
        "total_tarif": total_global,
        "total_temporaire": total_temporaire,
        "total_en_attente": total_en_attente,
        "rdvs_traites": rdvs_traites,
        "rdvs_acceptes": rdvs_acceptes,
        "rdvs_refuses": rdvs_refuses,
        "rdvs_termines": rdvs_termines,
        "has_rdv_temporaires": rdv_temporaires.exists(),
        "has_rdv_definitifs": len(rdv_definitifs_en_attente) > 0,
    }
    
    return render(request, 'coach_app/dashboard.html', context)

@login_required
def supprimer_rendez_vous(request, rdv_id):
    if request.method == 'POST':
        try:
            # Essayer de supprimer un RDV temporaire d'abord
            rdv_temp = RDVTemporaire.objects.get(id=rdv_id, user=request.user)
            rdv_temp.delete()
            messages.success(request, "Rendez-vous temporaire supprimé avec succès.")
            return redirect('coach:votre_rendez_vous')
            
        except RDVTemporaire.DoesNotExist:
            # Si ce n'est pas un RDV temporaire, essayer un RDV définitif
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
            # Récupérer le RDV à modifier
            rdv = RendezVous.objects.get(id=rdv_id, user=request.user)
            
            # Rediriger vers la page de prise de RDV avec l'ID du RDV à modifier
            redirect_url = f"{reverse('coach:rendez_vous')}?exercice={rdv.exercice.id}&modifier=true&rdv_id={rdv.id}"
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

@login_required
def vider_reservation(request):
    if request.method == 'POST':
        try:
            # Supprimer tous les RDV temporaires de l'utilisateur
            rdv_count = SessionService.clear_temporary_appointments(request.user)
            
            messages.success(request, f"{rdv_count} créneau(x) temporaire(s) supprimé(s).")
            return redirect('coach:rendez_vous')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
            return redirect('coach:rendez_vous')
    
    return redirect('coach:rendez_vous')


# ===== VUES COACH =====

def coach_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est un coach"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_coach:
            messages.error(request, "Accès réservé aux coaches.")
            return redirect('coach:votre_rendez_vous')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@coach_required
def coach_dashboard(request):
    """Dashboard principal du coach - tous les rendez-vous"""
    from datetime import date
    
    # Rendez-vous en attente de validation
    rdv_en_attente = AppointmentService.get_pending_appointments()
    
    # Rendez-vous validés (futurs)
    rdv_valides = RendezVous.objects.filter(
        statut='valide',
        date__gte=date.today()
    ).select_related('user', 'exercice').order_by('date', 'heure')
    
    # Rendez-vous terminés (passés)
    rdv_termines = RendezVous.objects.filter(
        statut='termine'
    ).select_related('user', 'exercice').order_by('-date', '-heure')[:20]  # 20 derniers
    
    context = {
        'rdv_en_attente': rdv_en_attente,
        'rdv_valides': rdv_valides,
        'rdv_termines': rdv_termines,
        'total_en_attente': rdv_en_attente.count(),
        'total_valides': rdv_valides.count(),
        'total_termines': rdv_termines.count(),
    }
    
    return render(request, 'coach_app/coach/dashboard.html', context)


@login_required
@coach_required
def coach_historique(request):
    """Historique complet des rendez-vous"""
    from datetime import date
    
    # Tous les rendez-vous terminés
    rdv_termines = RendezVous.objects.filter(
        statut='termine'
    ).select_related('user', 'exercice').order_by('-date', '-heure')
    
    # Filtres
    client_id = request.GET.get('client')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if client_id:
        rdv_termines = rdv_termines.filter(user_id=client_id)
    
    if date_debut:
        try:
            rdv_termines = rdv_termines.filter(date__gte=date_debut)
        except:
            pass
    
    if date_fin:
        try:
            rdv_termines = rdv_termines.filter(date__lte=date_fin)
        except:
            pass
    
    # Liste des clients pour le filtre
    clients = User.objects.filter(rendez_vous__statut='termine').distinct().order_by('username')
    
    context = {
        'rdv_termines': rdv_termines,
        'clients': clients,
        'client_selectionne': client_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'coach_app/coach/historique.html', context)


@login_required
@coach_required
def coach_valider_rdv(request, rdv_id):
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            notes = request.POST.get('notes', '').strip()
            
            if action in ['valider', 'refuser', 'terminer', 'notes']:
                if action == 'valider':
                    rdv = CoachService.validate_appointment(rdv_id, 'valide', notes)
                    messages.success(request, f"✅ Rendez-vous de {rdv.user.username} validé avec succès.")
                elif action == 'refuser':
                    rdv = CoachService.validate_appointment(rdv_id, 'refuse', notes)
                    messages.success(request, f"❌ Rendez-vous de {rdv.user.username} refusé.")
                elif action == 'terminer':
                    rdv = CoachService.validate_appointment(rdv_id, 'termine', notes)
                    messages.success(request, f"✅ Séance de {rdv.user.username} marquée comme terminée.")
                elif action == 'notes' and notes:
                    rdv = CoachService.add_private_note(rdv_id, notes)
                    messages.success(request, f"📝 Note ajoutée à l'historique pour {rdv.user.username}.")
            else:
                messages.error(request, f"Action non reconnue: {action}")
        except RendezVous.DoesNotExist:
            messages.error(request, "Rendez-vous non trouvé.")
    return redirect('coach:coach_details_rdv', rdv_id=rdv_id)


@login_required
@coach_required
def coach_details_rdv(request, rdv_id):
    """Détails d'un rendez-vous pour le coach"""
    try:
        rdv = RendezVous.objects.select_related('user', 'exercice').get(id=rdv_id)
        
        # Historique des séances du même client
        historique_client = RendezVous.objects.filter(
            user=rdv.user,
            statut='termine'
        ).exclude(id=rdv_id).order_by('-date', '-heure')[:5]
        
        # Historique des notes pour ce rendez-vous
        notes_historique = rdv.notes_historique.all().order_by('-date_creation')
        
        context = {
            'rdv': rdv,
            'historique_client': historique_client,
            'notes_historique': notes_historique,
        }
        
        return render(request, 'coach_app/coach/details_rdv.html', context)
        
    except RendezVous.DoesNotExist:
        messages.error(request, "Rendez-vous non trouvé.")
        return redirect('coach:coach_dashboard')


@login_required
@coach_required
def coach_statistiques(request):
    """Statistiques pour le coach"""
    from datetime import date, timedelta
    from django.db.models import Count, Sum
    
    # Statistiques générales
    stats = StatisticsService.get_coach_statistics()
    total_rdv = stats['total_appointments']
    rdv_en_attente = stats['pending_appointments']
    rdv_valides = RendezVous.objects.filter(statut='valide').count()
    rdv_termines = RendezVous.objects.filter(statut='termine').count()
    
    # Chiffre d'affaires
    ca_total = RendezVous.objects.filter(statut__in=['valide', 'termine']).aggregate(
        total=Sum('tarif')
    )['total'] or 0
    
    # Rendez-vous par mois (6 derniers mois)
    stats_mensuelles = []
    for i in range(6):
        mois_date = date.today() - timedelta(days=30*i)
        mois_debut = mois_date.replace(day=1)
        if i == 0:
            mois_fin = date.today()
        else:
            mois_fin = (mois_debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        rdv_mois = RendezVous.objects.filter(
            date__range=[mois_debut, mois_fin]
        ).count()
        
        ca_mois = RendezVous.objects.filter(
            date__range=[mois_debut, mois_fin],
            statut__in=['valide', 'termine']
        ).aggregate(total=Sum('tarif'))['total'] or 0
        
        stats_mensuelles.append({
            'mois': mois_debut.strftime('%B %Y'),
            'rdv_count': rdv_mois,
            'ca': ca_mois,
        })
    
    # Top clients
    top_clients = User.objects.filter(
        rendez_vous__statut='termine'
    ).annotate(
        rdv_count=Count('rendez_vous')
    ).order_by('-rdv_count')[:5]
    
    context = {
        'total_rdv': total_rdv,
        'rdv_en_attente': rdv_en_attente,
        'rdv_valides': rdv_valides,
        'rdv_termines': rdv_termines,
        'ca_total': ca_total,
        'stats_mensuelles': stats_mensuelles,
        'top_clients': top_clients,
    }
    
    return render(request, 'coach_app/coach/statistiques.html', context)


@login_required
def historique_rdv(request):
    """Historique des rendez-vous traités par le coach"""
    # Récupérer les RDV qui ont été validés, refusés ou terminés
    rdvs_traites = AppointmentService.get_appointment_history(request.user)
    
    # Calculer les statistiques
    rdvs_acceptes = rdvs_traites.filter(statut='valide').count()
    rdvs_refuses = rdvs_traites.filter(statut='refuse').count()
    rdvs_termines = rdvs_traites.filter(statut='termine').count()
    
    context = {
        'rdvs_traites': rdvs_traites,
        'rdvs_acceptes': rdvs_acceptes,
        'rdvs_refuses': rdvs_refuses,
        'rdvs_termines': rdvs_termines,
    }
    
    return render(request, 'coach_app/historique_rdv.html', context)

