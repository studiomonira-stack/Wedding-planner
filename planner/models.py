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

    def __str__(self):
        return f"{self.namn} - {self.user.username}"


class Tidslinje(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
