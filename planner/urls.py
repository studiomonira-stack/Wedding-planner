from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.checklist, name='checklist'),
    path('add/', views.add_checklist_item, name='add_checklist_item'),
    path('toggle/<int:item_id>/', views.toggle_checklist_item, name='toggle_checklist_item'),
    path('delete/<int:item_id>/', views.delete_checklist_item, name='delete_checklist_item'),
    path('budget/', views.budget, name='budget'),
    path('budget/add/', views.add_budget_post, name='add_budget_post'),
    path('budget/delete/<int:post_id>/', views.delete_budget_post, name='delete_budget_post'),
    path('gastlista/', views.gastlista, name='gastlista'),
    path('gastlista/add/', views.add_gast, name='add_gast'),
    path('gastlista/update/<int:gast_id>/', views.update_gast, name='update_gast'),
    path('gastlista/delete/<int:gast_id>/', views.delete_gast, name='delete_gast'),
    path('leverantorer/', views.leverantorer, name='leverantorer'),
    path('leverantorer/add/', views.add_leverantor, name='add_leverantor'),
    path('leverantorer/toggle/<int:lev_id>/', views.toggle_leverantor, name='toggle_leverantor'),
    path('leverantorer/delete/<int:lev_id>/', views.delete_leverantor, name='delete_leverantor'),
    path('tidslinje/', views.tidslinje, name='tidslinje'),
    path('tidslinje/add/', views.add_tidslinje, name='add_tidslinje'),
    path('tidslinje/delete/<int:tid_id>/', views.delete_tidslinje, name='delete_tidslinje'),
    path('galleri/', views.galleri, name='galleri'),
    path('galleri/add/', views.add_bild, name='add_bild'),
    path('galleri/delete/<int:bild_id>/', views.delete_bild, name='delete_bild'),
    path('fotograf/tidslinje/<int:kund_id>/', views.fotograf_tidslinje, name='fotograf_tidslinje'),
    path('fotograf/tidslinje/<int:kund_id>/ny/', views.fotograf_ny_handelse, name='fotograf_ny_handelse'),
    path('fotograf/tidslinje/<int:kund_id>/ta-bort/<int:handelse_id>/', views.fotograf_ta_bort_handelse, name='fotograf_ta_bort_handelse'),
    path('dashboard-embed/', views.dashboard_embed, name='dashboard_embed'),
   
    ]