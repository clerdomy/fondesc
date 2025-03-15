from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Contact(models.Model):
    """Model for storing contact form submissions"""
    SUBJECT_CHOICES = (
        ('general', _('General Information')),
        ('courses', _('Course Inquiries')),
        ('technical', _('Technical Support')),
        ('billing', _('Billing & Payments')),
        ('partnership', _('Partnership Opportunities')),
        ('other', _('Other')),
    )
    
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    subject = models.CharField(_('Subject'), max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField(_('Message'))
    ip_address = models.GenericIPAddressField(_('IP Address'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_read = models.BooleanField(_('Is Read'), default=False)
    
    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def mark_as_read(self):
        """Mark the contact submission as read"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])



class NewsletterSubscriber(models.Model):
    """Model for storing newsletter subscribers"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    def confirm_subscription(self):
        """Confirm the newsletter subscription"""
        if not self.confirmed_at:
            self.confirmed_at = timezone.now()
            self.confirmation_token = None
            self.save(update_fields=['confirmed_at', 'confirmation_token', 'updated_at'])
    
    def unsubscribe(self):
        """Unsubscribe from the newsletter"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'