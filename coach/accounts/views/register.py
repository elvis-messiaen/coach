from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
        else:
            User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, "Votre compte a été créé avec succès. Vous pouvez vous connecter.")
            return redirect('login')

    return render(request, 'registration/register.html')
