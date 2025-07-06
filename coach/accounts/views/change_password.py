from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        user = authenticate(request, username=request.user.username, password=current_password)
        
        if user is None:
            messages.error(request, 'Le mot de passe actuel est incorrect.')
            return redirect('coach:votre_rendez_vous')
        
        if new_password1 != new_password2:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            return redirect('coach:votre_rendez_vous')
        
        form = PasswordChangeForm(user, {
            'old_password': current_password,
            'new_password1': new_password1,
            'new_password2': new_password2
        })
        
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
            return redirect('coach:votre_rendez_vous')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur: {error}')
            return redirect('coach:votre_rendez_vous')
    
    return redirect('coach:votre_rendez_vous') 