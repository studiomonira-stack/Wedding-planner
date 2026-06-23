from accounts.models import Profil

def photographer_context(request):
    """Gör photographer tillgänglig i ALLA templates"""
    if request.user.is_authenticated:
        try:
            profil = Profil.objects.get(user=request.user)
            if profil.photographer:
                return {'photographer': profil.photographer}
        except Profil.DoesNotExist:
            pass
    return {'photographer': None}