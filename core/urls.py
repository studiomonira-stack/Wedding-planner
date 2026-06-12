from django.contrib import admin
from django.urls import path, include
from django.conf.urls import i18n

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('checklist/', include('planner.urls')),
    path('', include('accounts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]