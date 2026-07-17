from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
import secrets
from .models import Photographer, Brollop
from .models import PartnerPage
from .models import LeverantorProfil
from .models import Booking

@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('name', 'whop_email', 'whop_affiliate_id', 'has_account', 'is_active', 'created_at')
    search_fields = ('name', 'whop_email')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)
    actions = ['skapa_konton']
    
    def has_account(self, obj):
        return obj.user is not None
    has_account.boolean = True
    has_account.short_description = 'Har konto'
    
    def skapa_konton(self, request, queryset):
        skapade = []
        for f in queryset.filter(user__isnull=True):
            base_username = f.name.lower().replace(' ', '_')[:20]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            password = secrets.token_urlsafe(10)
            user = User.objects.create_user(username=username, email=f.whop_email or '', password=password)
            f.user = user
            f.is_active = True
            f.save()
            skapade.append(f"{f.name}: {username} / {password}")
        
        self.message_user(request, f"Skapade {len(skapade)} konton:\n" + "\n".join(skapade))
    
    skapa_konton.short_description = "Skapa användarkonton för valda fotografer"

admin.site.register(Brollop)


@admin.register(PartnerPage)
class PartnerPageAdmin(admin.ModelAdmin):
    list_display = ('photographer', 'slug', 'is_active')
    search_fields = ('photographer__name', 'slug')
    list_filter = ('is_active',)

@admin.register(LeverantorProfil)
class LeverantorProfilAdmin(admin.ModelAdmin):
    list_display = ('name', 'leverantor_type', 'email', 'is_active', 'created_at')
    list_filter = ('leverantor_type', 'is_active')
    search_fields = ('name', 'email')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'leverantor', 'date', 'time', 'status')
    list_filter = ('status', 'leverantor')
    search_fields = ('customer_name', 'customer_email')