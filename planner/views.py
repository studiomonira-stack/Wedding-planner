from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje, Galleri 
from .forms import PhotographerStep1Form, PhotographerStep2Form
from .models import Photographer
from django.core.mail import send_mail  # <-- Lägg till denna rad
from django.contrib.auth.models import User


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
    poster = BudgetPost.objects.filter(user=request.user).order_by('kategori')
    kategorier = BudgetPost.KATEGORIER

    total_budget = sum(p.budgeterat for p in poster)
    total_faktiskt = sum(p.faktiskt for p in poster)
    differens = total_budget - total_faktiskt

    for post in poster:
        post.diff = post.budgeterat - post.faktiskt

    return render(request, 'planner/budget.html', {
        'poster': poster,
        'kategorier': kategorier,
        'total_budget': total_budget,
        'total_faktiskt': total_faktiskt,
        'differens': differens,
    })


@login_required
def add_budget_post(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        beskrivning = request.POST.get('beskrivning', '')
        budgeterat = request.POST.get('budgeterat', 0)
        faktiskt = request.POST.get('faktiskt', 0)
        BudgetPost.objects.create(
            user=request.user,
            kategori=kategori,
            beskrivning=beskrivning,
            budgeterat=budgeterat,
            faktiskt=faktiskt,
        )
    return redirect('budget')


@login_required
def delete_budget_post(request, post_id):
    post = get_object_or_404(BudgetPost, id=post_id, user=request.user)
    post.delete()
    return redirect('budget')

@login_required
def gastlista(request):
    gaster = Gast.objects.filter(user=request.user).order_by('namn')
    svar_alternativ = Gast.SVAR

    antal_kommer = sum(g.antal for g in gaster if g.svar == 'kommer')
    antal_invagen = sum(g.antal for g in gaster if g.svar == 'invagen')
    antal_kommer_inte = sum(g.antal for g in gaster if g.svar == 'kommer_inte')
    totalt_antal = sum(g.antal for g in gaster)

    return render(request, 'planner/gastlista.html', {
        'gaster': gaster,
        'svar_alternativ': svar_alternativ,
        'antal_kommer': antal_kommer,
        'antal_invagen': antal_invagen,
        'antal_kommer_inte': antal_kommer_inte,
        'totalt_antal': totalt_antal,
    })

@login_required
def add_gast(request):
    if request.method == 'POST':
        Gast.objects.create(
            user=request.user,
            namn=request.POST.get('namn'),
            email=request.POST.get('email', ''),
            telefon=request.POST.get('telefon', ''),
            antal=request.POST.get('antal', 1),
            bord=request.POST.get('bord', ''),
            notering=request.POST.get('notering', ''),
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
def leverantorer(request):
    leverantorer_lista = Leverantor.objects.filter(user=request.user).order_by('kategori', 'namn')
    kategorier = Leverantor.KATEGORIER

    return render(request, 'planner/leverantorer.html', {
        'leverantorer': leverantorer_lista,
        'kategorier': kategorier,
    })


@login_required
def add_leverantor(request):
    if request.method == 'POST':
        Leverantor.objects.create(
            user=request.user,
            namn=request.POST.get('namn'),
            kategori=request.POST.get('kategori'),
            kontaktperson=request.POST.get('kontaktperson', ''),
            email=request.POST.get('email', ''),
            telefon=request.POST.get('telefon', ''),
            pris=request.POST.get('pris', 0),
            notering=request.POST.get('notering', ''),
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
def tidslinje(request):
    handelser = Tidslinje.objects.filter(user=request.user).order_by('tid', 'ordning')
    return render(request, 'planner/tidslinje.html', {
        'handelser': handelser,
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
def galleri(request):
    bilder = Galleri.objects.filter(user=request.user).order_by('-skapad')
    kategorier = Galleri.KATEGORIER
    return render(request, 'planner/galleri.html', {
        'bilder': bilder,
        'kategorier': kategorier,
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

         # <--- NY KOD: KONTROLLERA GDPR-KRYSSRUTAN --->
        if not request.POST.get('accept_privacy'):
            form = PhotographerStep1Form(request.POST, request.FILES)
            form.add_error(None, "Du måste godkänna integritetspolicyn för att fortsätta.")
            return render(request, 'planner/register_photographer_base.html', {
                'step_content': 'planner/register_photographer_step1.html',
                'form': form
            })
        # <-------------------------------------------->

        form = PhotographerStep1Form(request.POST, request.FILES)  # <-- Använd Step1Form
        if form.is_valid():
            photographer = form.save(commit=False)
            photographer.is_active = False
            photographer.save()
            request.session['temp_photographer_id'] = photographer.id
            
            # Visa Steg 2
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
        if photographer_id:
            try:
                photographer = Photographer.objects.get(id=photographer_id)
                whop_email = request.POST.get('whop_email')
                if whop_email:
                    photographer.whop_email = whop_email
                    photographer.save()
                    
                                       # --- SKICKA MEJL TILL DIG (ADMIN) ---
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

    # --- Hämta fotografen ---
    photographer_id = request.session.get('temp_photographer_id')
    photographer = None
    if photographer_id:
        try:
            photographer = Photographer.objects.get(id=photographer_id)
        except Photographer.DoesNotExist:
            pass

    # --- STEG 4: KLART! ---
    if photographer and photographer.whop_affiliate_id:
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