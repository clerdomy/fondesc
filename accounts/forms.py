from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import NotificationSettings

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        
        # Custom placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'phone_number')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


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

