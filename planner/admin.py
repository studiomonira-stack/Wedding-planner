from django.contrib import admin
from .models import Brollop
from .models import Photographer

@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('name', 'whop_email', 'whop_affiliate_id', 'is_active', 'created_at')
    search_fields = ('name', 'whop_email')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Brollop)
admin.site.register(Photographer, PhotographerAdmin)