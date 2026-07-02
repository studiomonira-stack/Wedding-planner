from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('login-embed/', views.login_embed, name='login_embed'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('webhook/whop/', views.whop_webhook, name='whop_webhook'),
    path('skapa-par/', views.skapa_par, name='skapa_par'),
    path('kop/', views.kop, name='kop'),
    path('welcome/', views.welcome, name='welcome'),
    path('landing-test/', views.landing_test, name='landing_test'),
]