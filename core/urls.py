from django import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import i18n
from django.conf import settings
from django.conf.urls.static import static
from planner import views as planner_views
from planner.views import partner_page
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from planner import views as planner_views

sitemaps = {'static': StaticViewSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('checklist/', include('planner.urls')),
    path('', include('accounts.urls')),
    path('register-partner/', planner_views.register_photographer, name='register_photographer'),
    path('privacy-policy/', planner_views.privacy_policy, name='privacy_policy'),
    path('partner-demo/', planner_views.partner_landing_demo, name='partner_landing_demo'),
    path('i18n/', include('django.conf.urls.i18n')), 
    path('rosetta/', include('rosetta.urls')),
    path('p/<slug:slug>/', partner_page, name='partner_page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('leverantor/<slug:slug>/boka/', planner_views.leverantor_booking, name='leverantor_booking'),
]
from django.views.decorators.csrf import csrf_exempt

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


