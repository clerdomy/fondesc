from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:enrollment_id>/', views.payment_process, name='payment_process'),
    path('success/<int:enrollment_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:enrollment_id>/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
