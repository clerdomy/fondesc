from django.db import models
from django.utils.crypto import get_random_string
import os

# Modèl ki egziste deja
class SchoolLevel(models.TextChoices):
    PRIMARY = 'primary', 'Lekòl Primè'
    SECONDARY = 'secondary', 'Lekòl Segondè'

class Grade(models.TextChoices):
    # Lekòl Primè
    GRADE1 = 'grade1', '1ye Ane'
    GRADE2 = 'grade2', '2yèm Ane'
    GRADE3 = 'grade3', '3yèm Ane'
    GRADE4 = 'grade4', '4yèm Ane'
    GRADE5 = 'grade5', '5yèm Ane'
    GRADE6 = 'grade6', '6yèm Ane'
    # Lekòl Segondè
    GRADE7 = 'grade7', '7yèm Ane'
    GRADE8 = 'grade8', '8yèm Ane'
    GRADE9 = 'grade9', '9yèm Ane'
    GRADE10 = 'grade10', '10yèm Ane'
    GRADE11 = 'grade11', '11yèm Ane'
    GRADE12 = 'grade12', '12yèm Ane'

class Gender(models.TextChoices):
    MALE = 'male', 'Gason'
    FEMALE = 'female', 'Fi'
    OTHER = 'other', 'Lòt'

class Relationship(models.TextChoices):
    PARENT = 'parent', 'Paran'
    GUARDIAN = 'guardian', 'Responsab Legal'
    OTHER = 'other', 'Lòt'

class AcademicYear(models.TextChoices):
    YEAR_2023_2024 = '2023-2024', '2023-2024'
    YEAR_2024_2025 = '2024-2025', '2024-2025'

class ReferralSource(models.TextChoices):
    FRIEND = 'friend', 'Zanmi oswa Fanmi'
    SOCIAL_MEDIA = 'social_media', 'Rezo Sosyal'
    WEBSITE = 'website', 'Sit Entènèt'
    NEWSPAPER = 'newspaper', 'Jounal'
    OTHER = 'other', 'Lòt'

class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'An Atant'
    DOCUMENTS_REQUIRED = 'documents_required', 'Dokiman Obligatwa'
    DOCUMENTS_RECEIVED = 'documents_received', 'Dokiman Resevwa'
    UNDER_REVIEW = 'under_review', 'Anba Revizyon'
    INTERVIEW_SCHEDULED = 'interview_scheduled', 'Entèvyou Pwograme'
    ACCEPTED = 'accepted', 'Aksepte'
    REJECTED = 'rejected', 'Rejte'
    WAITLISTED = 'waitlisted', 'Nan Lis Datant'

def generate_access_token():
    """Jenere yon token inik pou aksè a aplikasyon an"""
    return get_random_string(length=32)

class Enrollment(models.Model):
    # Enfòmasyon elèv
    school_level = models.CharField(max_length=20, choices=SchoolLevel.choices)
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_dob = models.DateField()
    student_gender = models.CharField(max_length=10, choices=Gender.choices)
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    grade_applying = models.CharField(max_length=10, choices=Grade.choices)
    academic_year = models.CharField(max_length=10, choices=AcademicYear.choices)
    
    # Enfòmasyon paran/responsab
    parent_first_name = models.CharField(max_length=100)
    parent_last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=Relationship.choices)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    
    # Enfòmasyon adisyonèl
    special_needs = models.BooleanField(default=False)
    special_needs_details = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200)
    how_heard = models.CharField(max_length=20, choices=ReferralSource.choices, blank=True, null=True)
    
    # Enfòmasyon sistèm
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=30, 
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DOCUMENTS_REQUIRED
    )
    status_notes = models.TextField(blank=True, null=True)
    
    # Token pou aksè sekirize
    access_token = models.CharField(max_length=32, default=generate_access_token, unique=True)
    
    def __str__(self):
        return f"{self.student_first_name} {self.student_last_name} - {self.get_grade_applying_display()}"
    
    def get_document_upload_url(self):
        """Retounen URL pou telechaje dokiman yo"""
        from django.urls import reverse
        return reverse('document_upload', kwargs={'token': self.access_token})
    
    def get_application_status_url(self):
        """Retounen URL pou verifye estati aplikasyon an"""
        from django.urls import reverse
        return reverse('application_status', kwargs={'token': self.access_token})
    
    class Meta:
        verbose_name = "Enskripsyon"
        verbose_name_plural = "Enskripsyon yo"

def document_upload_path(instance, filename):
    """Defini chemen pou telechaje dokiman yo"""
    # Kreye yon chemen ki gen ladan ID enskripsyon an ak non elèv la
    enrollment = instance.enrollment
    student_name = f"{enrollment.student_first_name}_{enrollment.student_last_name}"
    # Kreye yon chemen tankou: documents/12345_john_doe/birth_certificate.pdf
    return os.path.join('documents', f"{enrollment.id}_{student_name}", filename)

class DocumentType(models.TextChoices):
    BIRTH_CERTIFICATE = 'birth_certificate', 'Sètifika Nesans'
    REPORT_CARD = 'report_card', 'Kanè'
    VACCINATION_CARD = 'vaccination_card', 'Kat Vaksinasyon'
    PASSPORT_PHOTO = 'passport_photo', 'Foto Paspò'
    PROOF_OF_RESIDENCE = 'proof_of_residence', 'Prèv Rezidans'
    RECOMMENDATION_LETTER = 'recommendation_letter', 'Lèt Rekòmandasyon'
    OTHER = 'other', 'Lòt Dokiman'

class Document(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(upload_to=document_upload_path)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.enrollment}"
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    class Meta:
        verbose_name = "Dokiman"
        verbose_name_plural = "Dokiman yo"