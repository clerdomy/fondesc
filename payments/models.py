from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from courses.models import Course
import uuid

class Payment(models.Model):
    """Model to store payment information"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('cancelled', _('Cancelled')),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('card', _('Credit/Debit Card')),
        ('moncash', _('MonCash')),
        ('lajancash', _('Lajan Cash')),
        ('bank', _('Bank Transfer')),
        ('remittance', _('Remittance')),
        ('cash', _('Cash')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='HTG')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Payment method specific fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # For mobile money
    bank_reference = models.CharField(max_length=100, blank=True, null=True)  # For bank transfers
    remittance_info = models.JSONField(blank=True, null=True)  # For Western Union/MoneyGram
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)  # For uploaded receipts
    
    # Stripe specific fields
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Verification fields
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # Only auto-enroll if payment is completed AND it's a card payment
        # Other payment methods require manual verification
        if self.status == 'completed' and self.payment_method == 'card':
            from courses.models import Enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                user=self.user,
                course=self.course,
                defaults={'is_paid': True}
            )
            if not created and not enrollment.is_paid:
                enrollment.is_paid = True
                enrollment.save()
        
        super().save(*args, **kwargs)


class Discount(models.Model):
    """Model for discount codes"""
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=0)  # 0 means unlimited
    current_uses = models.PositiveIntegerField(default=0)
    
    # Discount can be applied to specific courses or all courses
    courses = models.ManyToManyField(Course, blank=True, related_name='discounts')
    
    class Meta:
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_to:
            return False
        
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, price):
        """Calculate the discount amount for a given price"""
        if not self.is_valid:
            return 0
        
        if self.amount:
            return min(self.amount, price)  # Don't discount more than the price
        
        if self.percentage:
            return (self.percentage / 100) * price
        
        return 0


class PaymentNotification(models.Model):
    """Model to store payment notifications from payment gateways"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)
    notification_data = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('Payment Notification')
        verbose_name_plural = _('Payment Notifications')
        ordering = ['-received_at']
    
    def __str__(self):
        return f"Notification for {self.payment.id} - {self.notification_type}"

