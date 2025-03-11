from django.contrib import admin

from .models import (
    StudentProfile, Document, MethodPayment, Course, LearningObjective, CurriculumYear, 
    Semester, CourseSubject, AdmissionRequirement, Faculty, Testimonial, 
    CareerOpportunity, CareerStat, TuitionFee, PaymentOption, FinancialAid,
    ContactMessage
)

# Configuração para o modelo StudentProfile
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user__first_name", "user__last_name", "user__email", "phone", "birth_date", "gender", "city")
    list_filter = ("gender", "city")
    search_fields = ("user__first_name", "user__last_name", "user__email", "phone")
    pass


# Configuração para o modelo Document
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "id_document", "diploma", "transcript", "photo")
    search_fields = ("student__user__first_name", "student__last_name")
    list_filter = ("student__city",)

# Configuração para o modelo Payment
@admin.register(MethodPayment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "payment_option", "payment_method", "terms_accepted")
    list_filter = ("payment_option", "payment_method", "terms_accepted")
    search_fields = ("student__user__first_name", "student__last_name", "mobile_code")

# Configuração para o modelo Course
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "modality", "duration", "start_dates")
    list_filter = ("level", "modality")
    search_fields = ("name",)

# Configuração para LearningObjective
@admin.register(LearningObjective)
class LearningObjectiveAdmin(admin.ModelAdmin):
    list_display = ("course", "description")
    search_fields = ("course__name", "description")

# Configuração para CurriculumYear
@admin.register(CurriculumYear)
class CurriculumYearAdmin(admin.ModelAdmin):
    list_display = ("course", "year_number", "title")
    search_fields = ("course__name", "title")

# Configuração para Semester
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("curriculum_year", "semester_number")
    list_filter = ("semester_number",)

# Configuração para CourseSubject
@admin.register(CourseSubject)
class CourseSubjectAdmin(admin.ModelAdmin):
    list_display = ("semester", "name")
    search_fields = ("name",)

# Configuração para AdmissionRequirement
@admin.register(AdmissionRequirement)
class AdmissionRequirementAdmin(admin.ModelAdmin):
    list_display = ("course", "requirement_type", "description")
    list_filter = ("requirement_type",)
    search_fields = ("course__name", "description")

# Configuração para Faculty
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "specialties")
    search_fields = ("name", "specialties")

# Configuração para Testimonial
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("course", "author_name", "author_title")
    search_fields = ("author_name", "author_title")

# Configuração para CareerOpportunity
@admin.register(CareerOpportunity)
class CareerOpportunityAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "examples")
    search_fields = ("title", "examples")

# Configuração para CareerStat
@admin.register(CareerStat)
class CareerStatAdmin(admin.ModelAdmin):
    list_display = ("course", "value", "label")
    search_fields = ("label",)

# Configuração para TuitionFee
@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    list_display = ("course", "description", "amount")
    search_fields = ("description",)

# Configuração para PaymentOption
@admin.register(PaymentOption)
class PaymentOptionAdmin(admin.ModelAdmin):
    list_display = ("course", "description")
    search_fields = ("description",)

# Configuração para FinancialAid
@admin.register(FinancialAid)
class FinancialAidAdmin(admin.ModelAdmin):
    list_display = ("course", "title")
    search_fields = ("title",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'first_name', 'last_name', 'email', 'created_at', 'is_read', 'is_replied')
    list_filter = ('subject', 'is_read', 'is_replied', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True)
    mark_as_replied.short_description = "Mark selected messages as replied"