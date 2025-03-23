from django.urls import path
from . import views

urlpatterns = [
    path('enskripsyon/', views.enrollment_view, name='enrollment'),
    path('dokiman/<str:token>/', views.document_upload_view, name='document_upload'),
    path('dokiman/<str:token>/efase/<int:document_id>/', views.delete_document_view, name='delete_document'),
    path('estati/<str:token>/', views.application_status_view, name='application_status'),
    path('lekol-segonde/', views.high_school_view, name='high_school'),
    # Lòt URL yo...
]