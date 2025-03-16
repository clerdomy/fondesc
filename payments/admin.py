from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages

from .models import Payment, Discount, PaymentNotification
from courses.models import Enrollment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'course_link', 'amount', 'currency', 'payment_method', 'status', 'payment_date', 'verification_status')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('user__username', 'user__email', 'course__title', 'transaction_id')
    readonly_fields = ('id', 'payment_date', 'last_updated', 'ip_address', 'user_agent', 'verified_by', 'verified_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'course', 'amount', 'currency', 'status', 'payment_method', 'transaction_id')
        }),
        ('Payment Details', {
            'fields': ('phone_number', 'bank_reference', 'remittance_info', 'receipt_file', 'stripe_payment_intent_id', 'stripe_payment_method_id')
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'last_updated')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at')
        }),
        ('Additional Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    actions = ['verify_payments', 'mark_as_failed']
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def course_link(self, obj):
        url = reverse('admin:courses_course_change', args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.title)
    course_link.short_description = 'Course'
    
    def verification_status(self, obj):
        if obj.verified_by:
            return format_html('<span style="color: green;">Verified by {} on {}</span>', 
                              obj.verified_by.username, 
                              obj.verified_at.strftime('%Y-%m-%d %H:%M'))
        elif obj.payment_method == 'card' and obj.status == 'completed':
            return format_html('<span style="color: blue;">Auto-verified (Card Payment)</span>')
        elif obj.status == 'pending':
            return format_html('<span style="color: orange;">Awaiting Verification</span>')
        else:
            return format_html('<span style="color: red;">Not Verified</span>')
    verification_status.short_description = 'Verification'
    
    def verify_payments(self, request, queryset):
        """Admin action to verify payments and enroll students"""
        verified_count = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'completed'
                payment.verified_by = request.user
                payment.verified_at = timezone.now()
                payment.save()
                
                # Enroll the student
                enrollment, created = Enrollment.objects.get_or_create(
                    user=payment.user,
                    course=payment.course,
                    defaults={'is_paid': True}
                )
                if not created and not enrollment.is_paid:
                    enrollment.is_paid = True
                    enrollment.save()
                
                verified_count += 1
        
        if verified_count:
            self.message_user(request, f"{verified_count} payments verified and students enrolled.", messages.SUCCESS)
        else:
            self.message_user(request, "No payments were verified. Make sure to select pending payments.", messages.WARNING)
    verify_payments.short_description = "Verify selected payments and enroll students"
    
    def mark_as_failed(self, request, queryset):
        """Admin action to mark payments as failed"""
        failed_count = queryset.filter(status='pending').update(status='failed')
        if failed_count:
            self.message_user(request, f"{failed_count} payments marked as failed.", messages.SUCCESS)
        else:
            self.message_user(request, "No pending payments were found to mark as failed.", messages.WARNING)
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount_value', 'is_active', 'valid_from', 'valid_to', 'usage_count', 'is_currently_valid')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    filter_horizontal = ('courses',)
    
    def discount_value(self, obj):
        if obj.amount:
            return f"{obj.currency} {obj.amount}"
        elif obj.percentage:
            return f"{obj.percentage}%"
        return "-"
    discount_value.short_description = 'Discount Value'
    
    def usage_count(self, obj):
        return f"{obj.current_uses} / {obj.max_uses if obj.max_uses > 0 else '∞'}"
    usage_count.short_description = 'Usage'
    
    def is_currently_valid(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    is_currently_valid.short_description = 'Valid'


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_link', 'notification_type', 'received_at', 'processed')
    list_filter = ('notification_type', 'processed', 'received_at')
    readonly_fields = ('payment', 'notification_type', 'notification_data', 'received_at')
    
    def payment_link(self, obj):
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html('<a href="{}">{}</a>', url, obj.payment.id)
    payment_link.short_description = 'Payment'

