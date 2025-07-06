from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre mot de passe a été changé avec succès.")
        return response
    
    def form_invalid(self, form):
        return super().form_invalid(form) 