from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Authentication URLs
authentication_patterns = [
    path('enskri/', views.RegisterView.as_view(), name='register'),  # Register
    path('konsekte/', views.CustomLoginView.as_view(), name='login'), # Login
    path('dekonekte/', views.logout_view, name='logout'),  # Logout
]

# User Profile & Dashboard URLs
user_patterns = [
    path('profil/', views.ProfileView.as_view(), name='profile'),  # User profile
    path('panèl/', views.dashboard_view, name='dashboard'),  # Dashboard
    path('kour-mwen/', views.my_courses_view, name='my_courses'),  # My courses
    path('panèl-enstriktè/', views.instructor_dashboard_view, name='instructor_dashboard'),  # Instructor dashboard
]

# Password Management URLs
password_patterns = [
    path('chanjman-modpas/', views.password_change_view, name='password_change'),  # Change password
    
    path('rekipere-modpas/', auth_views.PasswordResetView.as_view(  # Password reset
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/kont/rekipere-modpas-fini/'
    ), name='password_reset'),

    path('rekipere-modpas-fini/', auth_views.PasswordResetDoneView.as_view(  # Password reset done
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('konfime-modpas/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(  # Password reset confirmation
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('modpas-reyisi/', auth_views.PasswordResetCompleteView.as_view(  # Password reset complete
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# Notification Settings URLs
settings_patterns = [
    path('anviwonman-notifikasyon/', views.notification_settings_view, name='notification_settings'),  # Notification settings
]

# Combine all URL patterns
urlpatterns = (
    authentication_patterns + 
    user_patterns + 
    password_patterns + 
    settings_patterns
)
