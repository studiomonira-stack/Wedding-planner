from django.utils import translation

class ForceLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang', '')
        if lang:
            translation.activate(lang)
            request.session['_language'] = lang
        
        # Om språk finns i session, använd det
        if not lang and '_language' in request.session:
            translation.activate(request.session['_language'])
        
        response = self.get_response(request)
        return response