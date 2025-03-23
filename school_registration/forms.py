from django import forms
from .models import Enrollment, Document, SchoolLevel, Grade, Gender, Relationship, AcademicYear, ReferralSource, DocumentType

class EnrollmentForm(forms.ModelForm):
    agree_terms = forms.BooleanField(required=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'school_level', 'student_first_name', 'student_last_name', 'student_dob', 
            'student_gender', 'previous_school', 'grade_applying', 'academic_year',
            'parent_first_name', 'parent_last_name', 'relationship', 'phone', 
            'email', 'address', 'special_needs', 'special_needs_details',
            'emergency_contact', 'how_heard'
        ]
        widgets = {
            'student_dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'special_needs_details': forms.Textarea(attrs={'rows': 3}),
            'special_needs': forms.RadioSelect(choices=[(True, 'Wi'), (False, 'Non')]),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Deskripsyon opsyonèl'}),
        }