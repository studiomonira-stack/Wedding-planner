from linecache import cache

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from planner.models import ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje, Galleri
import json
import secrets


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')


def register(request):
    # Registrering sker endast via Whop-köp
    return redirect('landing')


@login_required
def dashboard(request):
    # Checklista
    total_checklist = ChecklistItem.objects.filter(user=request.user).count()
    klara_checklist = ChecklistItem.objects.filter(user=request.user, klar=True).count()
    checklist_procent = int((klara_checklist / total_checklist * 100)) if total_checklist > 0 else 0
    checklist_items = ChecklistItem.objects.filter(user=request.user).order_by('kategori', '-skapad')[:4]
    checklist_remaining = total_checklist - klara_checklist

    # Budget
    poster = BudgetPost.objects.filter(user=request.user)
    total_budget = sum(p.budgeterat for p in poster)
    total_faktiskt = sum(p.faktiskt for p in poster)
    resultat = total_budget - total_faktiskt
    budget_procent = int((total_faktiskt / total_budget * 100)) if total_budget > 0 else 0
    budget_kvar = 100 - budget_procent if budget_procent < 100 else 0

    # Gäster
    gaster = Gast.objects.filter(user=request.user)
    antal_kommer = sum(g.antal for g in gaster if g.svar == 'kommer')
    antal_invagen = sum(g.antal for g in gaster if g.svar == 'invagen')
    antal_kommer_inte = sum(g.antal for g in gaster if g.svar == 'kommer_inte')
    totalt_gaster = sum(g.antal for g in gaster)
    gaster_procent = int((antal_kommer / totalt_gaster * 100)) if totalt_gaster > 0 else 0

    # Leverantörer
    leverantorer = Leverantor.objects.filter(user=request.user)
    antal_leverantorer = leverantorer.count()
    antal_bokade = leverantorer.filter(bokat=True).count()
    antal_ej_bokade = antal_leverantorer - antal_bokade
    leverantor_procent = int((antal_bokade / antal_leverantorer * 100)) if antal_leverantorer > 0 else 0

    # Tidslinje
    handelser = Tidslinje.objects.filter(user=request.user).order_by('tid')[:5]
    antal_handelser = Tidslinje.objects.filter(user=request.user).count()

    # Galleri
    galleri_bilder = Galleri.objects.filter(user=request.user).order_by('-skapad')[:4]
    galleri_antal = Galleri.objects.filter(user=request.user).count()

    return render(request, 'accounts/dashboard.html', {
        'total_checklist': total_checklist,
        'klara_checklist': klara_checklist,
        'checklist_procent': checklist_procent,
        'total_budget': total_budget,
        'total_faktiskt': total_faktiskt,
        'resultat': resultat,
        'budget_procent': budget_procent,
        'budget_kvar': budget_kvar,
        'antal_kommer': antal_kommer,
        'antal_invagen': antal_invagen,
        'antal_kommer_inte': antal_kommer_inte,
        'totalt_gaster': totalt_gaster,
        'gaster_procent': gaster_procent,
        'antal_leverantorer': antal_leverantorer,
        'antal_bokade': antal_bokade,
        'antal_ej_bokade': antal_ej_bokade,
        'leverantor_procent': leverantor_procent,
        'handelser': handelser,
        'antal_handelser': antal_handelser,
        'galleri_bilder': galleri_bilder,
        'galleri_antal': galleri_antal,
        'checklist_items': checklist_items,
        'checklist_remaining': checklist_remaining,
    })

@csrf_exempt
def whop_webhook(request):
    """Tar emot köp från Whop och skapar användarkonto automatiskt"""
    
    try:
        data = json.loads(request.body)
        email = data.get('customer', {}).get('email', '')
        
        if not email:
            return JsonResponse({'error': 'Email saknas'}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email.split('@')[0]}
        )

        if created:
            password = secrets.token_urlsafe(12)
            user.set_password(password)
            user.save()
            
            # Spara lösenordet temporärt i 1 timme
            from django.core.cache import cache
            cache.set(f'password_{email}', password, timeout=3600)
        else:
            # Om användaren redan finns, hämta eller skapa nytt lösenord
            password = secrets.token_urlsafe(12)
            user.set_password(password)
            user.save()
            from django.core.cache import cache
            cache.set(f'password_{email}', password, timeout=3600)

        return JsonResponse({'status': 'ok', 'created': created}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

        
def welcome(request):
    email = request.GET.get('email', '')
    from django.core.cache import cache
    password = cache.get(f'password_{email}', '')
    
    if password:
        cache.delete(f'password_{email}')
        return render(request, 'accounts/welcome.html', {
            'email': email,
            'password': password,
        })
    else:
        return redirect('login')