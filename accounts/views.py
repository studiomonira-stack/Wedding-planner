from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Profil
from planner.models import Brollop, ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje, Galleri
import json
import secrets


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            
            roll = request.POST.get('roll', 'par')
            Profil.objects.create(user=user, telefon=form.cleaned_data.get('phone'), roll=roll)
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    profil, created = Profil.objects.get_or_create(user=request.user, defaults={'roll': 'planerare'})
    
    # TVINGA alla till planerare tills vi hittar felet
    profil.roll = 'planerare'
    profil.save()
    
    brollop_lista = Brollop.objects.filter(planerare=request.user)
    return render(request, 'accounts/planerare_dashboard.html', {
        'brollop_lista': brollop_lista,
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
            
            from django.core.cache import cache
            cache.set(f'password_{email}', password, timeout=3600)
        else:
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


@login_required
def skapa_par(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if username and email and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profil.objects.create(user=user, roll='par', planerare=request.user)
            return redirect('dashboard')
    
    return render(request, 'accounts/skapa_par.html')