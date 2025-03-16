from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Extended user model for additional profile information"""
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # User type choices
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    
    # Additional fields for instructors
    expertise = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class NotificationSettings(models.Model):
    """Model for storing user notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_course_updates = models.BooleanField(default=True, help_text="Receive emails about course updates")
    email_new_courses = models.BooleanField(default=True, help_text="Receive emails about new courses")
    email_promotions = models.BooleanField(default=True, help_text="Receive promotional emails")
    email_certificate = models.BooleanField(default=True, help_text="Receive emails when you earn a certificate")
    email_newsletter = models.BooleanField(default=True, help_text="Receive our weekly newsletter")
    browser_notifications = models.BooleanField(default=True, help_text="Receive browser notifications")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification settings for {self.user.username}"

@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    """Create notification settings for new users"""
    if created:
        NotificationSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_notification_settings(sender, instance, **kwargs):
    """Save notification settings when user is updated"""
    if hasattr(instance, 'notification_settings'):
        instance.notification_settings.save()
    else:
        NotificationSettings.objects.create(user=instance)


