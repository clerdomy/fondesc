from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import NotificationSettings

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
   
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form"""
    class Meta:
        model = User
        fields = ('username', 'password')

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'phone_number')
       


class NotificationSettingsForm(forms.ModelForm):
    """Form for updating notification settings"""
    class Meta:
        model = NotificationSettings
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'email_course_updates': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
            'email_new_courses': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
            'email_promotions': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
            'email_certificate': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
            'email_newsletter': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
            'browser_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary'}),
        }

