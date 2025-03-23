from django.contrib import admin
from django.utils.html import format_html
from .models import Enrollment, Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'enrollment', 'uploaded_at', 'is_verified', 'document_link')
    list_filter = ('document_type', 'is_verified', 'uploaded_at')
    search_fields = ('enrollment__student_first_name', 'enrollment__student_last_name', 'description')
    
    def document_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Wè Dokiman</a>', obj.file.url)
        return '-'
    document_link.short_description = 'Lyen Dokiman'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_first_name', 'student_last_name', 'school_level', 
                    'grade_applying', 'status', 'created_at')
    list_filter = ('school_level', 'grade_applying', 'academic_year', 'status')
    search_fields = ('student_first_name', 'student_last_name', 'parent_first_name', 
                     'parent_last_name', 'email', 'phone')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Enfòmasyon Elèv', {
            'fields': ('school_level', 'student_first_name', 'student_last_name', 
                       'student_dob', 'student_gender', 'previous_school', 
                       'grade_applying', 'academic_year')
        }),
        ('Enfòmasyon Paran/Responsab', {
            'fields': ('parent_first_name', 'parent_last_name', 'relationship', 
                       'phone', 'email', 'address')
        }),
        ('Enfòmasyon Adisyonèl', {
            'fields': ('special_needs', 'special_needs_details', 'emergency_contact', 
                       'how_heard')
        }),
        ('Estati Aplikasyon', {
            'fields': ('status', 'status_notes')
        }),
        ('Enfòmasyon Aksè', {
            'fields': ('access_token',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('access_token',)
    
    def view_documents(self, obj):
        count = obj.documents.count()
        if count:
            return format_html('<a href="{}?enrollment__id__exact={}" target="_blank">{} Dokiman</a>', 
                              '/admin/yourapp/document/', obj.id, count)
        return '0 Dokiman'
    view_documents.short_description = 'Dokiman yo'