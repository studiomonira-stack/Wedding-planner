from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    ROLLER = [
        ('par', 'Brudpar'),
        ('planerare', 'Planerare'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20, blank=True)
    roll = models.CharField(max_length=10, choices=ROLLER, default='par')
    planerare = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='par')
    utgangsdatum = models.DateField(null=True, blank=True)
    photographer = models.ForeignKey('planner.Photographer', on_delete=models.SET_NULL, null=True, blank=True, related_name='kunder')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_roll_display()})"