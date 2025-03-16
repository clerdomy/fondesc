from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:course_id>/', views.payment_process_view, name='payment_process'),
    path('confirm/', views.process_payment, name='process_payment'),
    path('apply-discount/', views.apply_discount, name='apply_discount'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('confirmation/<uuid:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('history/', views.payment_history, name='payment_history'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/<str:provider>/', views.payment_webhook, name='payment_webhook'),
]

