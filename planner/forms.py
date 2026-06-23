from django import forms
from .models import Photographer

class PhotographerStep1Form(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = ['name', 'logo', 'primary_color', 'accent_color']  # Endast dessa i Steg 1!
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
        }

class PhotographerStep2Form(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = ['whop_affiliate_id']  # Endast detta i Steg 2!