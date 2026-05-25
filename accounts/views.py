from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from planner.models import ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from planner.models import ChecklistItem, BudgetPost, Gast
import json
import secrets
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    # Checklista
    total_checklist = ChecklistItem.objects.filter(user=request.user).count()
    klara_checklist = ChecklistItem.objects.filter(user=request.user, klar=True).count()
    checklist_procent = int((klara_checklist / total_checklist * 100)) if total_checklist > 0 else 0

    # Budget
    poster = BudgetPost.objects.filter(user=request.user)
    total_budget = sum(p.budgeterat for p in poster)
    total_faktiskt = sum(p.faktiskt for p in poster)
    resultat = total_budget - total_faktiskt

    # Gäster
    gaster = Gast.objects.filter(user=request.user)
    antal_kommer = sum(g.antal for g in gaster if g.svar == 'kommer')
    antal_invagen = sum(g.antal for g in gaster if g.svar == 'invagen')
    antal_kommer_inte = sum(g.antal for g in gaster if g.svar == 'kommer_inte')
    totalt_gaster = sum(g.antal for g in gaster)
    # Leverantörer
    leverantorer = Leverantor.objects.filter(user=request.user)
    antal_leverantorer = leverantorer.count()
    antal_bokade = leverantorer.filter(bokat=True).count()
    antal_ej_bokade = antal_leverantorer - antal_bokade
        # Tidslinje
    handelser = Tidslinje.objects.filter(user=request.user).order_by('tid')
    forsta_handelse = handelser.first()
    sista_handelse = handelser.last()
    antal_handelser = handelser.count()

    return render(request, 'accounts/dashboard.html', {
        'total_checklist': total_checklist,
        'klara_checklist': klara_checklist,
        'checklist_procent': checklist_procent,
        'total_budget': total_budget,
        'total_faktiskt': total_faktiskt,
        'resultat': resultat,
        'antal_kommer': antal_kommer,
        'antal_invagen': antal_invagen,
        'antal_kommer_inte': antal_kommer_inte,
        'totalt_gaster': totalt_gaster,
                'antal_leverantorer': antal_leverantorer,
        'antal_bokade': antal_bokade,
        'antal_ej_bokade': antal_ej_bokade,
                'forsta_handelse': forsta_handelse,
        'sista_handelse': sista_handelse,
        'antal_handelser': antal_handelser,
    })

@csrf_exempt
def whop_webhook(request):
    """Tar emot köp från Whop och skapar användarkonto automatiskt"""
    
    # Verifiera att anropet kommer från Whop
    secret = request.headers.get('X-Whop-Secret', '')
    if secret != 'WHOP_HEMLIG_NYCKEL':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        email = data.get('customer', {}).get('email', '')
        
        if not email:
            return JsonResponse({'error': 'Email saknas'}, status=400)

        # Skapa användare om den inte redan finns
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
            }
        )

        if created:
            # Sätt ett slumpat lösenord
            password = secrets.token_urlsafe(12)
            user.set_password(password)
            user.save()
            
            # Här kan du skicka välkomstmail senare
            print(f"✅ Ny användare skapad: {email} | Lösenord: {password}")

        return JsonResponse({'status': 'ok', 'created': created}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)