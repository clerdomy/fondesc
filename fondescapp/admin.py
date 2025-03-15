from django.contrib import admin
from .models import Contact, NewsletterSubscriber

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject_display', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']
    
    def subject_display(self, obj):
        return obj.get_subject_display()
    subject_display.short_description = 'Subject'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'is_read')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at', 'confirmed_at')
    list_filter = ('is_active', 'created_at', 'confirmed_at')
    search_fields = ('email', 'name')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'confirmation_token', 'confirmed_at')
    date_hierarchy = 'created_at'
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
    activate_subscribers.short_description = "Activate selected subscribers"
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_subscribers.short_description = "Deactivate selected subscribers"
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'is_active')
        }),
        ('Confirmation Details', {
            'fields': ('confirmation_token', 'confirmed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )

