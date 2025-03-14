from django.contrib import admin
from .models import Payment, Invoice

# Register Payment model with customization
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'payment_method', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('user__username', 'transaction_id')
    list_editable = ('status',)  # Allows editing status directly from list view
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)

    # Optional: Customize how fields are displayed in the detail view
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'enrollment', 'amount')
    #     }),
    #     ('Payment Details', {
    #         'fields': ('status', 'payment_method', 'transaction_id', 'payment_date')
    #     }),
    # )

# Register Invoice model with customization
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'created_at', 'due_date')
    list_filter = ('created_at', 'due_date')
    search_fields = ('invoice_number', 'payment__user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Optional: Customize how fields are displayed in the detail view
    # fieldsets = (
    #     (None, {
    #         'fields': ('payment', 'invoice_number')
    #     }),
    #     ('Dates', {
    #         'fields': ('created_at', 'due_date')
    #     }),
    # )

# If you prefer the simple registration without customization, you could just use:
# admin.site.register(Payment)
# admin.site.register(Invoice)