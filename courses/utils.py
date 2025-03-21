import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from django.utils import timezone

from .models import Course, Enrollment, CourseReview


def generate_certificate_pdf(certificate):
    """Generate a PDF certificate for a completed course"""
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Register fonts
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    pdfmetrics.registerFont(TTFont('Roboto', os.path.join(font_path, 'Roboto-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('RobotoBold', os.path.join(font_path, 'Roboto-Bold.ttf')))
    
    # Draw certificate border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(3)
    c.rect(0.5*inch, 0.5*inch, width-inch, height-inch, stroke=1, fill=0)
    
    # Draw decorative elements
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(1.5)
    c.rect(0.75*inch, 0.75*inch, width-1.5*inch, height-1.5*inch, stroke=1, fill=0)
    
    # Add logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width/2 - 1*inch, height - 2*inch, width=2*inch, height=1*inch)
    
    # Add certificate title
    c.setFont('RobotoBold', 36)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width/2, height - 2.5*inch, "CERTIFICADO DE CONCLUSÃO")
    
    # Add course name
    c.setFont('RobotoBold', 24)
    c.drawCentredString(width/2, height - 3.5*inch, certificate.course.title)
    
    # Add student name
    c.setFont('Roboto', 18)
    c.drawCentredString(width/2, height - 4.5*inch, 
                       f"Este certificado é concedido a")
    
    c.setFont('RobotoBold', 28)
    c.drawCentredString(width/2, height - 5.2*inch, 
                       f"{certificate.user.get_full_name() or certificate.user.username}")
    
    # Add completion text
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        'Normal',
        fontName='Roboto',
        fontSize=14,
        alignment=1,  # Center alignment
        textColor=colors.black,
    )
    
    completion_text = f"""
    por concluir com sucesso o curso online de <b>{certificate.course.title}</b>, 
    demonstrando dedicação e domínio dos conceitos e habilidades ensinados.
    """
    
    p = Paragraph(completion_text, style)
    p.wrapOn(c, width - 3*inch, height)
    p.drawOn(c, 1.5*inch, height - 6*inch)
    
    # Add date
    c.setFont('Roboto', 14)
    date_str = certificate.created_at.strftime("%d de %B de %Y")
    c.drawCentredString(width/2, height - 7*inch, f"Emitido em {date_str}")
    
    # Add certificate number
    c.setFont('Roboto', 10)
    c.drawCentredString(width/2, 1*inch, f"Certificado Nº: {certificate.certificate_number}")
    
    # Add signature
    c.setFont('RobotoBold', 14)
    c.drawCentredString(width/2, 2*inch, "João Silva")
    c.setFont('Roboto', 12)
    c.drawCentredString(width/2, 1.7*inch, "Diretor de Educação")
    c.drawCentredString(width/2, 1.4*inch, "PythonLearn")
    
    # Add verification text
    c.setFont('Roboto', 8)
    c.drawCentredString(width/2, 0.75*inch, 
                       f"Verifique a autenticidade deste certificado em: pythonlearn.com/verify/{certificate.certificate_number}")
    
    # Close the PDF object cleanly
    c.showPage()
    c.save()
    
    # Get the value of the BytesIO buffer and save it to the certificate
    buffer.seek(0)
    return buffer

def create_certificate(user, course):
    """Create a certificate for a completed course"""
    from courses.models import Certificate
    
    # Check if certificate already exists
    try:
        certificate = Certificate.objects.get(user=user, course=course)
        return certificate
    except Certificate.DoesNotExist:
        # Create new certificate
        certificate = Certificate.objects.create(
            user=user,
            course=course
        )
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate)
        
        # Save PDF to certificate
        certificate.file.save(
            f'certificate_{certificate.certificate_number}.pdf',
            ContentFile(pdf_buffer.getvalue())
        )
        
        return certificate
    

def rating_stars(rating):
    """Generate HTML for displaying star ratings"""
    stars = ""
    if rating is None:
        rating = 0

    for i in range(1, 6):
        if i <= rating:
            stars += '<i class="fas fa-star"></i>'
        elif i <= rating + 0.5:
            stars += '<i class="fas fa-star-half-alt"></i>'
        else:
            stars += '<i class="far fa-star"></i>'
    return stars, round(rating, 1)


def get_instructor_course(instructor):
    """Get the courses for an instructor"""
    return Course.objects.filter(instructor=instructor).count()

def get_instructor_students(instructor):
    """Get the total number of students for an instructor"""
    return Enrollment.objects.filter(course__instructor=instructor).count()

def get_instructor_rating(instructor):
    """Get the average rating for an instructor's courses"""
    reviews = CourseReview.objects.filter(course__instructor=instructor)
    total_rating = sum([review.rating for review in reviews])
    if reviews:
        return round(total_rating / len(reviews), 1)
    return 0.0

def get_instructor_reviews(instructor):
    """Get the number of reviews for an instructor's courses"""
    return CourseReview.objects.filter(course__instructor=instructor).count()

def get_instructor_courses(instructor):
    """Get the courses 2 for an instructor"""
    return Course.objects.filter(instructor=instructor)[:2]

def get_category_courses(category):
    """Get the courses 5 for a category"""
    return Course.objects.filter(category=category, is_published=True)[:5]




