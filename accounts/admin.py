from django.contrib import admin
from .models import Profil

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'photographer', 'utgangsdatum')
    list_filter = ('roll', 'photographer')
    search_fields = ('user__username', 'user__email')
