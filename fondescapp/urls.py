from django.urls import path
from fondescapp  import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sou-nou', views.about_view, name='about'), 
    path('kontakte', views.contact_view, name='contact'),
    path('politik/konfidansyalite/', views.privacy_policy_view, name='privacy_policy'),
    path('tem-de-sevis', views.terms_of_service_view, name='terms_of_service'),
    path('politik/bonbon/', views.cookie_policy_view, name='cookie_policy'), 
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/confirm/<str:token>/', views.newsletter_confirm, name='newsletter_confirm'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]