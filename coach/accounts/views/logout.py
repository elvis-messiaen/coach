from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    request.session.flush()
    
    storage = messages.get_messages(request)
    storage.used = True
    
    messages.info(request, "Vous êtes maintenant déconnecté.")
    return redirect('login')
