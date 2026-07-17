from django.db import models
from django.contrib.auth.models import User

class Brollop(models.Model):
    planerare = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brollop')
    namn = models.CharField(max_length=200)  # t.ex. "Sara & Johan"
    datum = models.DateField(null=True, blank=True)
    skapad = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.namn} ({self.planerare.username})"

class ChecklistItem(models.Model):
    KATEGORIER = [
        ('12_manader', '12 månader innan'),
        ('6_manader', '6 månader innan'),
        ('3_manader', '3 månader innan'),
        ('1_manad', '1 månad innan'),
        ('veckan', 'Veckan innan'),
        ('dagen', 'Bröllopsdagen'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    text = models.CharField(max_length=255)
    kategori = models.CharField(max_length=20, choices=KATEGORIER, default='12_manader')
    klar = models.BooleanField(default=False)
    skapad = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class BudgetPost(models.Model):
    KATEGORIER = [
        ('lokal', 'Lokal'),
        ('catering', 'Catering'),
        ('fotograf', 'Fotograf'),
        ('film', 'Film'),
        ('blommor', 'Blommor'),
        ('klader', 'Klänning & Kostym'),
        ('musik', 'Musik & Underhållning'),
        ('transport', 'Transport'),
        ('inbjudningar', 'Inbjudningar'),
        ('ringar', 'Ringar'),
        ('har_och_makeup', 'Hår & Makeup'),
        ('ovrigt', 'Övrigt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    kategori = models.CharField(max_length=30, choices=KATEGORIER)
    beskrivning = models.CharField(max_length=255, blank=True)
    budgeterat = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    faktiskt = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    skapad = models.DateTimeField(auto_now_add=True)
    ordning = models.PositiveIntegerField(default=0)  # NYTT!
    
    class Meta:
        ordering = ['ordning', 'kategori']  # NYTT!

    def __str__(self):
        return f"{self.get_kategori_display()} - {self.user.username}"


class Gast(models.Model):
    SVAR = [
        ('invagen', 'Inväntar svar'),
        ('kommer', 'Kommer'),
        ('kommer_inte', 'Kommer inte'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    namn = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telefon = models.CharField(max_length=20, blank=True)
    antal = models.PositiveIntegerField(default=1)
    svar = models.CharField(max_length=15, choices=SVAR, default='invagen')
    bord = models.CharField(max_length=50, blank=True)
    notering = models.TextField(blank=True)
    skapad = models.DateTimeField(auto_now_add=True)
    ordning = models.PositiveIntegerField(default=0)  # NYTT!
    
    class Meta:
        ordering = ['ordning', 'namn']  # NYTT!

    def __str__(self):
        return f"{self.namn} - {self.user.username}"


class Leverantor(models.Model):
    KATEGORIER = [
        ('fotograf', 'Fotograf'),
        ('film', 'Film'),
        ('florist', 'Florist'),
        ('musik', 'Musik & Underhållning'),
        ('catering', 'Catering'),
        ('lokal', 'Lokal'),
        ('transport', 'Transport'),
        ('klader', 'Klänning & Kostym'),
        ('har_makeup', 'Hår & Makeup'),
        ('inbjudningar', 'Inbjudningar'),
        ('ringar', 'Ringar'),
        ('ovrigt', 'Övrigt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    namn = models.CharField(max_length=100)
    kategori = models.CharField(max_length=30, choices=KATEGORIER)
    kontaktperson = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefon = models.CharField(max_length=20, blank=True)
    pris = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    bokat = models.BooleanField(default=False)
    notering = models.TextField(blank=True)
    skapad = models.DateTimeField(auto_now_add=True)
    ordning = models.PositiveIntegerField(default=0)

class Meta:
    ordering = ['ordning', 'kategori']

    def __str__(self):
        return f"{self.namn} - {self.user.username}"


class Tidslinje(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # <--- LÄGG TILL DENNA NYA RAD HÄR: --->
    fotograf = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tidslinjer_som_fotograf')
    # <------------------------------------->
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    tid = models.TimeField()
    aktivitet = models.CharField(max_length=255)
    plats = models.CharField(max_length=255, blank=True)
    ansvarig = models.CharField(max_length=100, blank=True)
    notering = models.TextField(blank=True)
    ordning = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['tid', 'ordning']

    def __str__(self):
        return f"{self.tid} - {self.aktivitet}"

class Galleri(models.Model):
    KATEGORIER = [
        ('klanning', 'Klänning'),
        ('kostym', 'Kostym'),
        ('blommor', 'Blommor'),
        ('dukning', 'Dukning'),
        ('foto', 'Fotoinspiration'),
        ('hår_makeup', 'Hår & Makeup'),
        ('inbjudningar', 'Inbjudningar'),
        ('tårta', 'Tårta'),
        ('ovrigt', 'Övrigt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brollop = models.ForeignKey(Brollop, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_items')
    bild = models.URLField(max_length=500)
    titel = models.CharField(max_length=100, blank=True)
    kategori = models.CharField(max_length=20, choices=KATEGORIER, default='ovrigt')
    notering = models.TextField(blank=True)
    skapad = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-skapad']

    def __str__(self):
        return self.titel or self.bild[:50]

class Photographer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    name = models.CharField(max_length=100, verbose_name="Företagsnamn")
    logo = models.URLField(max_length=500, blank=True, null=True, verbose_name="Logga (URL)")
    primary_color = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Navbar-färg (Hex-kod)")
    accent_color = models.CharField(max_length=7, default="#C7BDAE", verbose_name="Accentfärg (Hex-kod)")
    whop_email = models.EmailField(blank=True, null=True, verbose_name="Whop E-post")
    whop_affiliate_id = models.CharField(max_length=100, verbose_name="Whop Affiliate ID")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class PartnerPage(models.Model):
    photographer = models.OneToOneField(Photographer, on_delete=models.CASCADE, related_name='partner_page')
    slug = models.SlugField(unique=True, max_length=100)
    headline = models.CharField(max_length=200, blank=True, verbose_name="Rubrik")
    bio = models.TextField(blank=True, verbose_name="Kort presentation")
    
    # Länkar
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    tiktok_url = models.URLField(blank=True, verbose_name="TikTok")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    website_url = models.URLField(blank=True, verbose_name="Hemsida")
    
    # Egna länkar
    custom_link_1_url = models.URLField(blank=True, verbose_name="Extra länk 1")
    custom_link_1_text = models.CharField(max_length=100, blank=True, verbose_name="Text länk 1")
    custom_link_2_url = models.URLField(blank=True, verbose_name="Extra länk 2")
    custom_link_2_text = models.CharField(max_length=100, blank=True, verbose_name="Text länk 2")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Linktree: {self.photographer.name}"



class LeverantorProfil(models.Model):
    LEVERANTOR_TYPES = [
        ('jeweler', 'Ringförsäljare'),
        ('florist', 'Florist'),
        ('makeup', 'Makeup-artist'),
        ('venue', 'Lokal'),
        ('c'
        'atering', 'Catering'),
        ('music', 'Musik/DJ'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    leverantor_type = models.CharField(max_length=20, choices=LEVERANTOR_TYPES, default='jeweler')
    name = models.CharField(max_length=100, verbose_name="Företagsnamn")
    logo = models.URLField(max_length=500, blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#F7F4EF")
    accent_color = models.CharField(max_length=7, default="#C8A26B")
    background_image = models.URLField(max_length=500, blank=True, null=True, verbose_name="Bakgrundsbild (URL)")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True, verbose_name="Beskrivning")
    website = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    
    
    # Bokningsinställningar
    accept_bookings = models.BooleanField(default=False, verbose_name="Ta emot bokningar")
    booking_email = models.EmailField(blank=True, null=True, verbose_name="Email för bokningar")
    
    # Whop
    whop_affiliate_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Leverantör"
        verbose_name_plural = "Leverantörer"

    def __str__(self):
        return f"{self.name} ({self.get_leverantor_type_display()})"
    

class Booking(models.Model):
    BOOKING_TYPES = [
        ('consultation', 'Konsultation'),
        ('visit', 'Besök/Provning'),
        ('call', 'Videosamtal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Väntar på bekräftelse'),
        ('confirmed', 'Bekräftad'),
        ('completed', 'Genomförd'),
        ('cancelled', 'Avbokad'),
    ]
    
    leverantor = models.ForeignKey(LeverantorProfil, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=100, verbose_name="Namn")
    customer_email = models.EmailField(verbose_name="Email")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES, default='consultation')
    date = models.DateField(verbose_name="Datum")
    time = models.TimeField(verbose_name="Tid")
    message = models.TextField(blank=True, verbose_name="Meddelande")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.customer_name} – {self.date} {self.time}"