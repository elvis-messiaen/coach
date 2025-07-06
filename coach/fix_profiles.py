from django.contrib.auth.models import User
from coach_app.models import Profile

for user in User.objects.all():
    Profile.objects.get_or_create(user=user)
print("Tous les profils manquants ont été créés.") 