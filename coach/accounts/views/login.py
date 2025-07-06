from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    context = {
        'username_value': '',
        'password_value': ''
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        context['username_value'] = username
        context['password_value'] = ''

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}')
            
            # Rediriger les coaches vers leur dashboard
            if hasattr(user, 'profile') and user.profile.is_coach:
                return redirect('coach:coach_dashboard')
            else:
                return redirect('coach:accueil')
        else:
            messages.error(request, 'Identifiants invalides.')

    return render(request, 'registration/login.html', context)
