from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class StudentProfile(models.Model):
    # Relacionamento com o usuário padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campos de informações pessoais
    first_name = models.CharField(max_length=100, verbose_name="Non")
    last_name = models.CharField(max_length=100, verbose_name="Siyati")
    email = models.EmailField(unique=True, verbose_name="Imèl")
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
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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

class Payment(models.Model):
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

class FinancialAid(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="financial_aids")
    title = models.CharField(max_length=100, verbose_name="Tit")
    description = models.TextField(verbose_name="Deskripsyon")
    
    def __str__(self):
        return self.title