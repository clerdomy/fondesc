from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from  django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


import string 
import random

class StudentProfile(models.Model):
    # Relacionamento com o usuário padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="Telefòn")
    birth_date = models.DateField(verbose_name="Dat Nesans")
    GENDER_CHOICES = [
        ('male', 'Gason'),
        ('female', 'Fi'),
        ('other', 'Lòt'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Sèks")
    address = models.CharField(max_length=255, verbose_name="Adrès")
    city = models.CharField(max_length=100, verbose_name="Vil")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Kòd Postal")
    is_candidate = models.BooleanField(default=True, verbose_name="Kandidan")
    
    EDUCATION_LEVEL  = (
        ('Elementary-i', 'Elemantè I (1ª a 5è)'),
       ('elementary-ii', 'Elemantè II (6è a 9è)'),
       ('high-school', 'Segondè'),
       ('technical', 'Teknik'),
       ('undergraduate', 'Lisans'),
       ('graduate', 'Metriz'),
       ('doctorate', 'Doktè'),

    )
    education_level = models.CharField(max_length=100, choices=EDUCATION_LEVEL, blank=True, null=True, verbose_name="Nivèl Enseman")

    def clean(self):
        if not self.is_candidate and not self.user.is_active:
            # se nao é candidato, o usuário deve estar ativo
            raise ValidationError("user must be active" )
        
        elif self.is_candidate and self.user.is_active:
            self.user.is_active = False
            self.user.save()

    def create_user(self, email:str, first_name:str, last_name:str):
        # Cria um novo usuário com base nos dados do perfil do estudante
        password = ''.join(
            random.choices(
                string.ascii_letters + 
                string.digits, k=12
            )
        )
        self.user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        self.user.is_active = False
        self.user.save()
        
class Document(models.Model):
    # Campos para documentos
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="documents")
    
    id_document = models.FileField(
        upload_to='documents/id/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name="Dokiman Idantite"
    )
    diploma = models.FileField(
        upload_to='documents/diplomas/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name="Diplòm"
    )
    transcript = models.FileField(
        upload_to='documents/transcripts/',
        blank=True, null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name="Relve Nòt"
    )
    photo = models.FileField(
        upload_to='documents/photos/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        verbose_name="Foto"
    )
    
    def __str__(self):
        return f"Documents for {self.student}"

class MethodPayment(models.Model):
    # Campos para pagamento
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="payments")
    
    PAYMENT_OPTION_CHOICES = [
        ('full', 'Peman Konplè'),
        ('installment', 'Peman an Vèsman'),
    ]
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION_CHOICES, default='full', verbose_name="Opsyon Peman")
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Kat Kredi/Debi'),
        ('bank', 'Transfè Bank'),
        ('mobile', 'Peman Mobil (MonCash)'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Metòd Peman")
    
    # Campos para cartão de crédito
    card_number = models.CharField(max_length=19, blank=True, null=True, verbose_name="Nimewo Kat")
    card_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Non sou Kat")
    card_expiry = models.CharField(max_length=5, blank=True, null=True, verbose_name="Dat Ekspirasyon")  # MM/YY
    card_cvv = models.CharField(max_length=4, blank=True, null=True, verbose_name="CVV")
    
    # Campo para comprovante de transferência bancária
    bank_receipt = models.FileField(
        upload_to='payments/bank_receipts/',
        blank=True, null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name="Resi Transfè"
    )
    
    # Campo para código de confirmação de pagamento mobile
    mobile_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Kòd Konfimasyon")
    
    terms_accepted = models.BooleanField(default=False, verbose_name="Tèm Aksepte")

    def clean(self):
        # deve ter no mínimo uma opção de pagamento selecionada
        if not self.payment_option:
            raise ValidationError("You must select a payment option.")

        # se o pagamento é por cartão de crédito, todos os campos de cartão devem ser preenchidos
        if self.payment_option == 'card' and not all([self.card_number, self.card_name, self.card_expiry, self.card_cvv]):
            raise ValidationError("All card details must be provided if using a credit card.")
        
        # se o pagamento é por transferência bancária, o comprovante de transferência deve ser fornecido
        if self.payment_option == 'bank' and not self.bank_receipt:
            raise ValidationError("A bank receipt must be provided if using bank transfer.")
        
        # se o pagamento é por pagamento mobile, o código de confirmação deve ser fornecido
        if self.payment_option == 'mobile' and not self.mobile_code:
            raise ValidationError("A mobile confirmation code must be provided if using mobile payment.")
    
    

    def __str__(self):
        return f"Payment for {self.student}"

# Modelo para informações gerais do curso
class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Non Kou")
    LEVEL_CHOICES = [
        ('high-school', 'Segondè'),
        ('technical', 'Teknik'),
        ('undergraduate', 'Lisans'),
        ('graduate', 'Metriz'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Nivo")
    tagline = models.CharField(max_length=255, verbose_name="Slogan Kou") # Exemplo: "Fòme Lide, Fòme Kreyativite"
    duration = models.CharField(max_length=50, verbose_name="Dire") # Exemplo: "2 ane"
    start_dates = models.CharField(max_length=100, verbose_name="Kòmansman")  # Exemplo: "Janvye, Me, Septanm"
    MODALITY_CHOICES = [
        ('distance', 'A distans'),
        ('in-person', 'Prezansyèl'),
        ('hybrid', 'Ibrid'),
    ]
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, verbose_name="Modalite")
    brochure = models.FileField(
        upload_to='brochures/',
        blank=True, null=True,
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name="Bwochi"
    )
    overview = models.TextField(verbose_name="Apèsi Kou") # Exemplo: "Kou sa ofri yon fòmasyon ki fòme lide nan domèn teknoloji."
    
    def __str__(self):
        return self.name

# Modelo para objetivos de aprendizagem
class LearningObjective(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="learning_objectives")
    description = models.CharField(max_length=255, verbose_name="Objektif Aprantisaj")
    
    def __str__(self):
        return self.description

# Modelo para currículo (anos e semestres)
class CurriculumYear(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="curriculum_years")
    year_number = models.PositiveIntegerField(verbose_name="Ane")
    title = models.CharField(max_length=50, verbose_name="Tit Ane", default="Premye Ane")
    
    def __str__(self):
        return f"{self.title} - {self.course.name}"

class Semester(models.Model):
    curriculum_year = models.ForeignKey(CurriculumYear, on_delete=models.CASCADE, related_name="semesters")
    SEMESTER_CHOICES = [
        (1, 'Premye Semès'),
        (2, 'Dezyèm Semès'),
    ]
    semester_number = models.PositiveIntegerField(choices=SEMESTER_CHOICES, verbose_name="Semès")
    
    def __str__(self):
        return f"Semès {self.semester_number} - {self.curriculum_year}"

class CourseSubject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100, verbose_name="Non Matyè")
    
    def __str__(self):
        return self.name

# Modelo para requisitos de admissão
class AdmissionRequirement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="admission_requirements")
    REQUIREMENT_TYPE_CHOICES = [
        ('basic', 'Kondisyon Debaz'),
        ('document', 'Dokiman Obligatwa'),
    ]
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPE_CHOICES, verbose_name="Tip Kondisyon")
    description = models.CharField(max_length=255, verbose_name="Deskripsyon")
    
    def __str__(self):
        return self.description

# Modelo para professores
class Faculty(models.Model):
    course = models.ManyToManyField(Course, related_name="faculty_members")
    name = models.CharField(max_length=100, verbose_name="Non")
    title = models.CharField(max_length=100, verbose_name="Tit")
    bio = models.TextField(verbose_name="Biyografi")
    photo = models.ImageField(upload_to='faculty/', verbose_name="Foto")
    specialties = models.CharField(max_length=255, verbose_name="Espesyalite")  # Exemplo: "Jesyon Estratejik,Lidèchip"
    
    def __str__(self):
        return self.name

# Modelo para depoimentos
class Testimonial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="testimonials")
    content = models.TextField(verbose_name="Kontni")
    author_name = models.CharField(max_length=100, verbose_name="Non Otè")
    author_title = models.CharField(max_length=100, verbose_name="Tit Otè")  # Exemplo: "Gradye 2022, Direktè Operasyon"
    author_photo = models.ImageField(upload_to='testimonials/', verbose_name="Foto Otè")
    
    def __str__(self):
        return f"Temwayaj pa {self.author_name}"

# Modelo para oportunidades de carreira
class CareerOpportunity(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="career_opportunities")
    title = models.CharField(max_length=100, verbose_name="Tit")
    description = models.TextField(verbose_name="Deskripsyon")
    examples = models.CharField(max_length=255, verbose_name="Egzanp")  # Exemplo: "Direktè Operasyon,Jesyonè Pwodwi"
    
    def __str__(self):
        return self.title

# Modelo para estatísticas de carreira
class CareerStat(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="career_stats")
    value = models.CharField(max_length=10, verbose_name="Valè")  # Exemplo: "92%"
    label = models.CharField(max_length=100, verbose_name="Etikèt")
    
    def __str__(self):
        return self.label

# Modelo para informações de investimento
class TuitionFee(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tuition_fees")
    description = models.CharField(max_length=100, verbose_name="Deskripsyon")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montan (HTG)")
    
    def __str__(self):
        return f"{self.description} - {self.amount} HTG"

class PaymentOption(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payment_options")
    description = models.CharField(max_length=100, verbose_name="Deskripsyon")
    
    def __str__(self):
        return self.description


class ContactMessage(models.Model):
    """Model for contact form messages"""
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    subject = models.CharField(_("Subject"), max_length=100, choices=[
        ('general', _('General Information')),
        ('admissions', _('Admissions')),
        ('courses', _('Course Information')),
        ('technical', _('Technical Support')),
        ('partnership', _('Partnership')),
        ('other', _('Other')),
    ])
    message = models.TextField(_("Message"))
    privacy_agree = models.BooleanField(_("Privacy Agreement"), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_read = models.BooleanField(_("Is Read"), default=False)
    is_replied = models.BooleanField(_("Is Replied"), default=False)
    
    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.first_name} {self.last_name}"

class ScholarshipInterest(models.Model):
    """Model for scholarship interest form submissions"""
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    scholarship_type = models.CharField(_("Scholarship Type"), max_length=50, choices=[
        ('merit', _('Merit Scholarship')),
        ('need', _('Need-Based Scholarship')),
        ('community', _('Community Service Scholarship')),
        ('special', _('Special Category Scholarship')),
        ('all', _('All Scholarships')),
    ])
    education_level = models.CharField(_("Education Level"), max_length=50, choices=[
        ('high_school', _('High School')),
        ('associate', _('Associate Degree')),
        ('bachelor', _('Bachelor\'s Degree')),
        ('master', _('Master\'s Degree')),
        ('other', _('Other')),
    ])
    program_interest = models.CharField(_("Program Interest"), max_length=50, choices=[
        ('administration', _('Administration')),
        ('accounting', _('Accounting')),
        ('pedagogy', _('Pedagogy')),
        ('technology', _('Technology')),
        ('marketing', _('Marketing')),
        ('hr', _('Human Resources')),
        ('other', _('Other')),
    ])
    comments = models.TextField(_("Comments"), blank=True, null=True)
    privacy_agree = models.BooleanField(_("Privacy Agreement"), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_contacted = models.BooleanField(_("Is Contacted"), default=False)
    
    class Meta:
        verbose_name = _("Scholarship Interest")
        verbose_name_plural = _("Scholarship Interests")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.scholarship_type}"


class Subscriber(models.Model):
    """Model for newsletter subscribers"""
    email = models.EmailField(_("Email"))
    privacy_agree = models.BooleanField(_("Privacy Agreement"), default=False)

    # Metadata
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class FinancialAid(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="financial_aids")
    title = models.CharField(max_length=100, verbose_name="Tit")
    description = models.TextField(verbose_name="Deskripsyon")
    
    def __str__(self):
        return self.title