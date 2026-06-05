from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChecklistItem, BudgetPost, Gast, Leverantor, Tidslinje, Galleri 


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