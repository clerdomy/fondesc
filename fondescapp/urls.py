from django.urls import path
from fondescapp  import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about', views.about_view, name='about'), 
    path('contact', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy'), 
     path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/confirm/<str:token>/', views.newsletter_confirm, name='newsletter_confirm'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]