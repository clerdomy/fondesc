from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from courses.models import Course, Enrollment

class Payment(models.Model):
    """Payment records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    # Payment status choices
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Payment method choices
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    transaction_id = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

class Invoice(models.Model):
    """Invoice records"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    
    def __str__(self):
        return self.invoice_number
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
