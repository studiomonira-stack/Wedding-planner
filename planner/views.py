from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje, Galleri 
from .forms import PhotographerStep1Form, PhotographerStep2Form
from .models import Photographer
from django.core.mail import send_mail  # <-- Lägg till denna rad
from django.contrib.auth.models import User
from accounts.models import Profil

@login_required
def checklist(request):
    items = ChecklistItem.objects.filter(user=request.user).order_by('kategori', '-skapad')
    kategorier = ChecklistItem.KATEGORIER
    
    kategorier_med_items = {}
    for value, name in kategorier:
        items_i_kategori = items.filter(kategori=value)
        if items_i_kategori.exists():
            kategorier_med_items[value] = {
                'name': name,
                'items': items_i_kategori
            }
    
    return render(request, 'planner/checklist.html', {
        'kategorier_med_items': kategorier_med_items,
        'kategorier': kategorier,
    })


@login_required
def add_checklist_item(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        kategori = request.POST.get('kategori')
        if text:
            ChecklistItem.objects.create(
                user=request.user,
                text=text,
                kategori=kategori,
            )
    return redirect('checklist')


@login_required
def toggle_checklist_item(request, item_id):
    item = get_object_or_404(ChecklistItem, id=item_id, user=request.user)
    item.klar = not item.klar
    item.save()
    return redirect('checklist')


@login_required
def delete_checklist_item(request, item_id):
    item = get_object_or_404(ChecklistItem, id=item_id, user=request.user)
    item.delete()
    return redirect('checklist')


@login_required
def budget(request):
    poster = BudgetPost.objects.filter(user=request.user).order_by('ordning', 'kategori')
    kategorier = BudgetPost.KATEGORIER

    total_budget = sum(p.budgeterat for p in poster)
    total_faktiskt = sum(p.faktiskt for p in poster)
    differens = total_budget - total_faktiskt

    for post in poster:
        post.diff = post.budgeterat - post.faktiskt

    # Hämta edit_id från URL:en (?edit=1)
    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_id = int(edit_id)
        except:
            edit_id = None    

    return render(request, 'planner/budget.html', {
        'poster': poster,
        'kategorier': kategorier,
        'total_budget': total_budget,
        'total_faktiskt': total_faktiskt,
        'differens': differens,
        'edit_id': edit_id, # Skicka med edit_id till mallen
    })


@login_required
def add_budget_post(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        beskrivning = request.POST.get('beskrivning', '')
        
        budgeterat_raw = request.POST.get('budgeterat', '0')
        faktiskt_raw = request.POST.get('faktiskt', '0')
        
        # Rensa bort mellanslag och kommatecken
        budgeterat_clean = budgeterat_raw.replace(' ', '').replace(',', '.')
        faktiskt_clean = faktiskt_raw.replace(' ', '').replace(',', '.')
        
        from decimal import Decimal, InvalidOperation
        
        try:
            budgeterat = Decimal(budgeterat_clean)
        except InvalidOperation:
            return render(request, 'planner/budget.html', {
                'error_message': 'Ange ett giltigt belopp (t.ex. 10000 eller 10000,50). Inga bokstäver.',
                'poster': BudgetPost.objects.filter(user=request.user).order_by('ordning', 'kategori'),
                'kategorier': BudgetPost.KATEGORIER,
            })
            
        try:
            faktiskt = Decimal(faktiskt_clean)
        except InvalidOperation:
            return render(request, 'planner/budget.html', {
                'error_message': 'Ange ett giltigt belopp (t.ex. 10000 eller 10000,50). Inga bokstäver.',
                'poster': BudgetPost.objects.filter(user=request.user).order_by('ordning', 'kategori'),
                'kategorier': BudgetPost.KATEGORIER,
            })
        
          # Hitta högsta ordning
        from django.db.models import Max
        max_ordning = BudgetPost.objects.filter(user=request.user).aggregate(Max('ordning'))['ordning__max'] or 0

        BudgetPost.objects.create(
            user=request.user,
            kategori=kategori,
            beskrivning=beskrivning,
            budgeterat=budgeterat,
            faktiskt=faktiskt,
            ordning=max_ordning + 1,
        )
    return redirect('budget')


@login_required
def delete_budget_post(request, post_id):
    post = get_object_or_404(BudgetPost, id=post_id, user=request.user)
    post.delete()
    return redirect('budget')

@login_required
def move_budget_up(request, post_id):
    post = get_object_or_404(BudgetPost, id=post_id, user=request.user)
    if post.ordning > 0:
        post.ordning -= 1
        post.save()
        # Flytta ner den som hade samma ordning
        BudgetPost.objects.filter(user=request.user, ordning=post.ordning).exclude(id=post.id).update(ordning=post.ordning + 1)
    return redirect('budget')


@login_required
def move_budget_down(request, post_id):
    post = get_object_or_404(BudgetPost, id=post_id, user=request.user)
    post.ordning += 1
    post.save()
    # Flytta upp den som hade samma ordning
    BudgetPost.objects.filter(user=request.user, ordning=post.ordning).exclude(id=post.id).update(ordning=post.ordning - 1)
    return redirect('budget')

@login_required
def update_budget_post(request, post_id):
    post = get_object_or_404(BudgetPost, id=post_id, user=request.user)
    if request.method == 'POST':
        post.kategori = request.POST.get('kategori')
        post.beskrivning = request.POST.get('beskrivning', '')
        post.budgeterat = request.POST.get('budgeterat', 0) or 0
        post.faktiskt = request.POST.get('faktiskt', 0) or 0
        post.save()
    return redirect('budget')

@login_required
def gastlista(request):
    gaster = Gast.objects.filter(user=request.user).order_by('ordning', 'namn')
    svar_alternativ = Gast.SVAR
    
    antal_kommer = sum(g.antal for g in gaster if g.svar == 'kommer')
    antal_invagen = sum(g.antal for g in gaster if g.svar == 'invagen')
    antal_kommer_inte = sum(g.antal for g in gaster if g.svar == 'kommer_inte')
    totalt_antal = sum(g.antal for g in gaster)
    
    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_id = int(edit_id)
        except:
            edit_id = None

    return render(request, 'planner/gastlista.html', {
        'gaster': gaster,
        'svar_alternativ': svar_alternativ,
        'antal_kommer': antal_kommer,
        'antal_invagen': antal_invagen,
        'antal_kommer_inte': antal_kommer_inte,
        'totalt_antal': totalt_antal,
        'edit_id': edit_id,
    })

@login_required
def add_gast(request):
    if request.method == 'POST':
        from django.db.models import Max
        max_ordning = Gast.objects.filter(user=request.user).aggregate(Max('ordning'))['ordning__max'] or 0
        
        Gast.objects.create(
            user=request.user,
            namn=request.POST.get('namn'),
            email=request.POST.get('email', ''),
            telefon=request.POST.get('telefon', ''),
            antal=request.POST.get('antal', 1),
            bord=request.POST.get('bord', ''),
            notering=request.POST.get('notering', ''),
            ordning=max_ordning + 1,
        )
    return redirect('gastlista')


@login_required
def update_gast(request, gast_id):
    gast = get_object_or_404(Gast, id=gast_id, user=request.user)
    if request.method == 'POST':
        gast.namn = request.POST.get('namn')
        gast.email = request.POST.get('email', '')
        gast.telefon = request.POST.get('telefon', '')
        gast.antal = request.POST.get('antal', 1)
        gast.bord = request.POST.get('bord', '')
        gast.notering = request.POST.get('notering', '')
        gast.svar = request.POST.get('svar', 'invagen')
        gast.save()
    return redirect('gastlista')


@login_required
def delete_gast(request, gast_id):
    gast = get_object_or_404(Gast, id=gast_id, user=request.user)
    gast.delete()
    return redirect('gastlista')

@login_required
def move_gast_up(request, gast_id):
    gast = get_object_or_404(Gast, id=gast_id, user=request.user)
    if gast.ordning > 0:
        gast.ordning -= 1
        gast.save()
        Gast.objects.filter(user=request.user, ordning=gast.ordning).exclude(id=gast.id).update(ordning=gast.ordning + 1)
    return redirect('gastlista')

@login_required
def move_gast_down(request, gast_id):
    gast = get_object_or_404(Gast, id=gast_id, user=request.user)
    gast.ordning += 1
    gast.save()
    Gast.objects.filter(user=request.user, ordning=gast.ordning).exclude(id=gast.id).update(ordning=gast.ordning - 1)
    return redirect('gastlista')

@login_required
def leverantorer(request):
    leverantorer_lista = Leverantor.objects.filter(user=request.user).order_by('ordning', 'kategori')
    kategorier = Leverantor.KATEGORIER

    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_id = int(edit_id)
        except:
            edit_id = None

    return render(request, 'planner/leverantorer.html', {
        'leverantorer': leverantorer_lista,
        'kategorier': kategorier,
        'edit_id': edit_id,
    })


@login_required
def add_leverantor(request):
    if request.method == 'POST':
        from django.db.models import Max
        max_ordning = Leverantor.objects.filter(user=request.user).aggregate(Max('ordning'))['ordning__max'] or 0
        
        Leverantor.objects.create(
            user=request.user,
            namn=request.POST.get('namn'),
            kategori=request.POST.get('kategori'),
            kontaktperson=request.POST.get('kontaktperson', ''),
            email=request.POST.get('email', ''),
            telefon=request.POST.get('telefon', ''),
            pris=request.POST.get('pris', 0) or 0,
            notering=request.POST.get('notering', ''),
            ordning=max_ordning + 1,
        )
    return redirect('leverantorer')


@login_required
def toggle_leverantor(request, lev_id):
    lev = get_object_or_404(Leverantor, id=lev_id, user=request.user)
    lev.bokat = not lev.bokat
    lev.save()
    return redirect('leverantorer')


@login_required
def delete_leverantor(request, lev_id):
    lev = get_object_or_404(Leverantor, id=lev_id, user=request.user)
    lev.delete()
    return redirect('leverantorer')

@login_required
def update_leverantor(request, lev_id):
    lev = get_object_or_404(Leverantor, id=lev_id, user=request.user)
    if request.method == 'POST':
        lev.namn = request.POST.get('namn')
        lev.kategori = request.POST.get('kategori')
        lev.kontaktperson = request.POST.get('kontaktperson', '')
        lev.pris = request.POST.get('pris', 0) or 0
        lev.notering = request.POST.get('notering', '')
        lev.save()
    return redirect('leverantorer')


@login_required
def move_leverantor_up(request, lev_id):
    lev = get_object_or_404(Leverantor, id=lev_id, user=request.user)
    if lev.ordning > 0:
        lev.ordning -= 1
        lev.save()
        Leverantor.objects.filter(user=request.user, ordning=lev.ordning).exclude(id=lev.id).update(ordning=lev.ordning + 1)
    return redirect('leverantorer')


@login_required
def move_leverantor_down(request, lev_id):
    lev = get_object_or_404(Leverantor, id=lev_id, user=request.user)
    lev.ordning += 1
    lev.save()
    Leverantor.objects.filter(user=request.user, ordning=lev.ordning).exclude(id=lev.id).update(ordning=lev.ordning - 1)
    return redirect('leverantorer')

@login_required
def tidslinje(request):
    handelser = Tidslinje.objects.filter(user=request.user).order_by('tid', 'ordning')
    
    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_id = int(edit_id)
        except:
            edit_id = None
    
    return render(request, 'planner/tidslinje.html', {
        'handelser': handelser,
        'edit_id': edit_id,
    })


@login_required
def add_tidslinje(request):
    if request.method == 'POST':
        Tidslinje.objects.create(
            user=request.user,
            tid=request.POST.get('tid'),
            aktivitet=request.POST.get('aktivitet'),
            plats=request.POST.get('plats', ''),
            ansvarig=request.POST.get('ansvarig', ''),
            notering=request.POST.get('notering', ''),
        )
    return redirect('tidslinje')


@login_required
def delete_tidslinje(request, tid_id):
    handelse = get_object_or_404(Tidslinje, id=tid_id, user=request.user)
    handelse.delete()
    return redirect('tidslinje')

@login_required
def update_tidslinje(request, tid_id):
    handelse = get_object_or_404(Tidslinje, id=tid_id, user=request.user)
    if request.method == 'POST':
        handelse.tid = request.POST.get('tid')
        handelse.aktivitet = request.POST.get('aktivitet')
        handelse.plats = request.POST.get('plats', '')
        handelse.ansvarig = request.POST.get('ansvarig', '')
        handelse.notering = request.POST.get('notering', '')
        handelse.save()
    return redirect('tidslinje')

@login_required
def galleri(request):
    bilder = Galleri.objects.filter(user=request.user).order_by('kategori', '-skapad')
    kategorier = Galleri.KATEGORIER
    
    # Gruppera bilder per kategori
    kategorier_med_bilder = {}
    for value, name in kategorier:
        bilder_i_kat = bilder.filter(kategori=value)
        if bilder_i_kat.exists():
            kategorier_med_bilder[value] = {
                'name': name,
                'bilder': bilder_i_kat
            }
    
    # Hämta edit_id från URL:en (?edit=1)
    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_id = int(edit_id)
        except:
            edit_id = None
            
    return render(request, 'planner/galleri.html', {
        'kategorier_med_bilder': kategorier_med_bilder,
        'kategorier': kategorier,
        'edit_id': edit_id,
    })


@login_required
def add_bild(request):
    if request.method == 'POST':
        bild_url = request.POST.get('bild')
        titel = request.POST.get('titel', '')
        kategori = request.POST.get('kategori', 'ovrigt')
        notering = request.POST.get('notering', '')
        if bild_url:
            Galleri.objects.create(
                user=request.user,
                bild=bild_url,
                titel=titel,
                kategori=kategori,
                notering=notering,
            )
    return redirect('galleri')


@login_required
def delete_bild(request, bild_id):
    bild = get_object_or_404(Galleri, id=bild_id, user=request.user)
    bild.delete()
    return redirect('galleri')

@login_required
def update_bild(request, bild_id):
    bild = get_object_or_404(Galleri, id=bild_id, user=request.user)
    if request.method == 'POST':
        bild.bild = request.POST.get('bild')
        bild.titel = request.POST.get('titel', '')
        bild.kategori = request.POST.get('kategori', 'ovrigt')
        bild.notering = request.POST.get('notering', '')
        bild.save()
    return redirect('galleri')

@login_required
def brollop_detail(request, brollop_id):
    from planner.models import Brollop
    brollop = get_object_or_404(Brollop, id=brollop_id)
    
    checklist_items = ChecklistItem.objects.filter(brollop=brollop)
    poster = BudgetPost.objects.filter(brollop=brollop)
    gaster = Gast.objects.filter(brollop=brollop)
    
    return render(request, 'planner/brollop_detail.html', {
        'brollop': brollop,
        'checklist_items': checklist_items,
        'poster': poster,
        'gaster': gaster,
    })


from .forms import PhotographerStep1Form, PhotographerStep2Form  # <-- Ändra importen!

def register_photographer(request):
    # --- STEG 1 ---
    if request.method == 'POST' and 'step1_submit' in request.POST:
        print("✅ Steg 1 mottaget!")

        # GDPR-kontroll
        if not request.POST.get('accept_privacy'):
            form = PhotographerStep1Form(request.POST, request.FILES)
            form.add_error(None, "Du måste godkänna integritetspolicyn för att fortsätta.")
            return render(request, 'planner/register_photographer_base.html', {
                'step_content': 'planner/register_photographer_step1.html',
                'form': form
            })

        form = PhotographerStep1Form(request.POST, request.FILES)
        if form.is_valid():
            photographer = form.save(commit=False)
            photographer.is_active = False
            photographer.save()
            request.session['temp_photographer_id'] = photographer.id
            
            form = PhotographerStep2Form(instance=photographer)
            return render(request, 'planner/register_photographer_base.html', {
                'step_content': 'planner/register_photographer_step2.html',
                'form': form,
                'photographer': photographer
            })
        else:
            print(f"❌ Fel: {form.errors}")

    # --- STEG 2 ---
    elif request.method == 'POST' and 'step2_submit' in request.POST:
        print("✅ Steg 2 mottaget!")
        
        photographer_id = request.session.get('temp_photographer_id')
        
        # Om sessionen är tom – försök hitta fotografen via e-post
        if not photographer_id:
            whop_email = request.POST.get('whop_email')
            if whop_email:
                try:
                    photographer = Photographer.objects.get(whop_email=whop_email)
                    photographer_id = photographer.id
                except Photographer.DoesNotExist:
                    pass
        
        if photographer_id:
            try:
                photographer = Photographer.objects.get(id=photographer_id)
                whop_email = request.POST.get('whop_email')
                if whop_email:
                    photographer.whop_email = whop_email
                    photographer.save()
                    
                    try:
                        send_mail(
                            subject='📸 Ny fotograf redo för Whop!',
                            message=f'Hej! En fotograf har precis slutfört Steg 2.\n\n'
                                    f'Namn: {photographer.name}\n'
                                    f'Whop-epost: {photographer.whop_email}\n'
                                    f'Logga: {photographer.logo.url if photographer.logo else "Ingen logga"}\n\n'
                                    f'Gå in i Whop och lägg till dem som affiliate nu!',
                            from_email='hej@brollopsplanner.se',
                            recipient_list=['hej@brollopsplanner.se'],
                            fail_silently=False,
                        )
                        print("📧 Mejlet skickades framgångsrikt!")
                    except Exception as e:
                        print(f"❌ MEJLKRASCH: {e}")
                        print(f"Detaljerad felinformation: {type(e).__name__}")
                    
                    return render(request, 'planner/register_photographer_base.html', {
                        'step_content': 'planner/registration_waiting.html',
                        'photographer': photographer
                    })
            except Photographer.DoesNotExist:
                pass

    # --- Hämta fotografen från sessionen ---
    photographer_id = request.session.get('temp_photographer_id')
    photographer = None
    if photographer_id:
        try:
            photographer = Photographer.objects.get(id=photographer_id)
        except Photographer.DoesNotExist:
            pass

        # --- STEG 4: KLART! ---
    if photographer and photographer.whop_affiliate_id:
        # Skapa användarkonto åt fotografen om det inte redan finns
        if not photographer.user:
            from django.contrib.auth.models import User
            import secrets
            
            # Skapa användarnamn baserat på företagsnamnet
            base_username = photographer.name.lower().replace(' ', '_')[:20]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Skapa lösenord
            password = secrets.token_urlsafe(10)
            
            user = User.objects.create_user(
                username=username,
                email=photographer.whop_email or '',
                password=password
            )
            photographer.user = user
            photographer.is_active = True
            photographer.save()
            
            # Skicka inloggningsuppgifter till fotografen
            try:
                send_mail(
                    subject='🎉 Ditt partnerkonto är klart!',
                    message=f'Hej {photographer.name}!\n\n'
                            f'Ditt partnerkonto är nu aktivt.\n\n'
                            f'Logga in på: https://www.brollopsplanner.se/login/\n'
                            f'Användarnamn: {username}\n'
                            f'Lösenord: {password}\n\n'
                            f'Logga in och gå till "Partner" i menyn för att se dina kunder.\n\n'
                            f'Välkommen!',
                    from_email='hej@brollopsplanner.se',
                    recipient_list=[photographer.whop_email],
                    fail_silently=False,
                )
                print(f"📧 Inloggningsuppgifter skickade till {photographer.whop_email}")
            except Exception as e:
                print(f"❌ Kunde inte skicka mail: {e}")
        
        return render(request, 'planner/register_photographer_base.html', {
            'step_content': 'planner/registration_complete.html',
            'photographer': photographer
        })

    # --- STEG 2 (visa igen) ---
    elif photographer:
        form = PhotographerStep2Form(instance=photographer)
        return render(request, 'planner/register_photographer_base.html', {
            'step_content': 'planner/register_photographer_step2.html',
            'form': form,
            'photographer': photographer
        })

    # --- STEG 1 ---
    else:
        form = PhotographerStep1Form()
        return render(request, 'planner/register_photographer_base.html', {
            'step_content': 'planner/register_photographer_step1.html',
            'form': form
        })

# ============================================
# NYA VYER FÖR FOTOGRAFENS TIDSLINJE
# ============================================

@login_required
def fotograf_tidslinje(request, kund_id):
    # Hitta kunden (brudparet)
    kund = get_object_or_404(User, id=kund_id)
    
    # Hämta alla tidslinje-händelser för detta par
    handelser = Tidslinje.objects.filter(user=kund).order_by('tid')
    
    return render(request, 'planner/fotograf_tidslinje.html', {
        'kund': kund,
        'handelser': handelser,
    })


@login_required
def fotograf_ny_handelse(request, kund_id):
    kund = get_object_or_404(User, id=kund_id)
    
    if request.method == 'POST':
        Tidslinje.objects.create(
            user=kund,                 # Koppla till kunden (brudparet)
            fotograf=request.user,     # Koppla till fotografen (den som loggat in)
            tid=request.POST.get('tid'),
            aktivitet=request.POST.get('aktivitet'),
            plats=request.POST.get('plats', ''),
            ansvarig=request.POST.get('ansvarig', ''),
            notering=request.POST.get('notering', ''),
            ordning=request.POST.get('ordning', 0)
        )
        return redirect('fotograf_tidslinje', kund_id=kund.id)
    
    return render(request, 'planner/fotograf_ny_handelse.html', {'kund': kund})


@login_required
def fotograf_ta_bort_handelse(request, kund_id, handelse_id):
    kund = get_object_or_404(User, id=kund_id)
    handelse = get_object_or_404(Tidslinje, id=handelse_id, user=kund)
    handelse.delete()
    return redirect('fotograf_tidslinje', kund_id=kund.id)

def privacy_policy(request):
    return render(request, 'planner/privacy_policy.html')

def partner_landing_demo(request):
    return render(request, 'planner/partner_landing.html')

@login_required
def dashboard_embed(request):
    try:
        profil = Profil.objects.get(user=request.user)
    except Profil.DoesNotExist:
        from datetime import date, timedelta
        utgang = date.today() + timedelta(days=730)
        profil = Profil.objects.create(user=request.user, roll='par', utgangsdatum=utgang)
    
    photographer = profil.photographer
    
    # Checklista
    total_checklist = ChecklistItem.objects.filter(user=request.user).count()
    klara_checklist = ChecklistItem.objects.filter(user=request.user, klar=True).count()
    checklist_procent = int((klara_checklist / total_checklist * 100)) if total_checklist > 0 else 0
    
    # Budget
    poster = BudgetPost.objects.filter(user=request.user)
    total_budget = sum(p.budgeterat for p in poster)
    total_faktiskt = sum(p.faktiskt for p in poster)
    budget_procent = int((total_faktiskt / total_budget * 100)) if total_budget > 0 else 0
    
    # Gäster
    gaster = Gast.objects.filter(user=request.user)
    antal_kommer = sum(g.antal for g in gaster if g.svar == 'kommer')
    totalt_gaster = sum(g.antal for g in gaster)
    gaster_procent = int((antal_kommer / totalt_gaster * 100)) if totalt_gaster > 0 else 0
    
    # Leverantörer
    leverantorer = Leverantor.objects.filter(user=request.user)
    antal_leverantorer = leverantorer.count()
    antal_bokade = leverantorer.filter(bokat=True).count()
    leverantor_procent = int((antal_bokade / antal_leverantorer * 100)) if antal_leverantorer > 0 else 0
    
    return render(request, 'planner/dashboard_embed.html', {
        'photographer': photographer,
        'total_checklist': total_checklist,
        'klara_checklist': klara_checklist,
        'checklist_procent': checklist_procent,
        'total_budget': total_budget,
        'total_faktiskt': total_faktiskt,
        'budget_procent': budget_procent,
        'totalt_gaster': totalt_gaster,
        'antal_kommer': antal_kommer,
        'gaster_procent': gaster_procent,
        'antal_leverantorer': antal_leverantorer,
        'antal_bokade': antal_bokade,
        'leverantor_procent': leverantor_procent,
        'antal_handelser': Tidslinje.objects.filter(user=request.user).count(),
        'galleri_antal': Galleri.objects.filter(user=request.user).count(),
    })

    # ============================================
# PARTNER / FOTOGRAF VIEWS
# ============================================

@login_required
def partner_dashboard(request):
    # Kolla att användaren är en fotograf
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    # Hämta fotografens kunder
    kunder = Profil.objects.filter(photographer=fotograf, roll='par')
    antal_kunder = kunder.count()
    
    # Kommande vigslar (bröllop kopplade till kunderna)
    from planner.models import Brollop
    kommande_brollop = Brollop.objects.filter(
        planerare__in=[k.user for k in kunder]
    ).order_by('datum')[:5]
    
    return render(request, 'planner/partner_dashboard.html', {
        'fotograf': fotograf,
        'antal_kunder': antal_kunder,
        'kunder': kunder.order_by('-user__date_joined')[:5],
        'kommande_brollop': kommande_brollop,
    })


@login_required
def partner_kunder(request):
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    kunder = Profil.objects.filter(photographer=fotograf, roll='par').select_related('user')
    
    return render(request, 'planner/partner_kunder.html', {
        'fotograf': fotograf,
        'kunder': kunder,
    })


@login_required
def partner_kund_detail(request, kund_id):
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    kund = get_object_or_404(Profil, id=kund_id, photographer=fotograf)
    
    # Kundens tidslinje
    tidslinje = Tidslinje.objects.filter(user=kund.user).order_by('tid')
    
    # Kundens galleri
    galleri = Galleri.objects.filter(user=kund.user).order_by('-skapad')
    kategorier = Galleri.KATEGORIER

    from planner.models import Brollop
    brollop = Brollop.objects.filter(planerare=kund.user).first()
    
    return render(request, 'planner/partner_kund_detail.html', {
        'fotograf': fotograf,
        'kund': kund,
        'tidslinje': tidslinje,
        'galleri': galleri,
        'kategorier': kategorier,
        'brollop': brollop,
    })


@login_required
def partner_add_tidslinje(request, kund_id):
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    kund = get_object_or_404(Profil, id=kund_id, photographer=fotograf)
    
    if request.method == 'POST':
        Tidslinje.objects.create(
            user=kund.user,
            fotograf=request.user,
            tid=request.POST.get('tid'),
            aktivitet=request.POST.get('aktivitet'),
            plats=request.POST.get('plats', ''),
            ansvarig=request.POST.get('ansvarig', ''),
            notering=request.POST.get('notering', ''),
            ordning=request.POST.get('ordning', 0)
        )
    return redirect('partner_kund_detail', kund_id=kund.id)


@login_required
def partner_add_galleri(request, kund_id):
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    kund = get_object_or_404(Profil, id=kund_id, photographer=fotograf)
    
    if request.method == 'POST':
        Galleri.objects.create(
            user=kund.user,
            bild=request.POST.get('bild'),
            titel=request.POST.get('titel', ''),
            kategori=request.POST.get('kategori', 'ovrigt'),
            notering=request.POST.get('notering', ''),
        )
    return redirect('partner_kund_detail', kund_id=kund.id)


@login_required
def partner_set_brollopsdatum(request, kund_id):
    fotograf = Photographer.objects.filter(user=request.user, is_active=True).first()
    if not fotograf:
        return redirect('dashboard')
    
    kund = get_object_or_404(Profil, id=kund_id, photographer=fotograf)
    
    if request.method == 'POST':
        from planner.models import Brollop
        
        # Hämta eller skapa bröllop
        brollop, created = Brollop.objects.get_or_create(
            planerare=kund.user,
            defaults={'namn': request.POST.get('namn', '')}
        )
        
        brollop.namn = request.POST.get('namn', brollop.namn)
        datum_str = request.POST.get('datum', '')
        if datum_str:
            brollop.datum = datum_str
        brollop.save()
    
    return redirect('partner_kund_detail', kund_id=kund.id)