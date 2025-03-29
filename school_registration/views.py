from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import Http404
from datetime import timedelta
from .models import Enrollment, Document, DocumentType
from .forms import EnrollmentForm, DocumentUploadForm

def enrollment_view(request):
    """
    View pou paj enskripsyon lekòl primè ak segondè
    """
    # Kalkile estatistik "live" yo
    available_spots = 45  # Ou ka ranplase sa a ak yon valè reyèl nan baz done
    today_registrations = Enrollment.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    # Kalkile jou ki rete nan peryòd enskripsyon an
    end_date = timezone.datetime(2024, 6, 30, tzinfo=timezone.get_current_timezone())
    days_remaining = (end_date.date() - timezone.now().date()).days
    if days_remaining < 0:
        days_remaining = 0
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            
            # Voye imèl konfimasyon
            try:
                document_upload_url = request.build_absolute_uri(enrollment.get_document_upload_url())
                application_status_url = request.build_absolute_uri(enrollment.get_application_status_url())
                
                email_message = f"""
                Mèsi pou enskripsyon ou, {enrollment.parent_first_name}.
                
                Nou pral kontakte ou nan 48 èdtan pou konfime enskripsyon {enrollment.student_first_name} {enrollment.student_last_name} pou {enrollment.get_grade_applying_display()}.
                
                Pou konplete aplikasyon ou, tanpri telechaje dokiman obligatwa yo nan lyen sa a:
                {document_upload_url}
                
                Ou ka verifye estati aplikasyon ou nenpòt ki lè nan lyen sa a:
                {application_status_url}
                
                Tanpri kenbe lyen sa yo an sekirite.
                
                Mèsi,
                Ekip Admisyon
                """
                
                send_mail(
                    subject='Konfimasyon Enskripsyon - Python Course Platform',
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[enrollment.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Anrejistre erè a men pa montre li bay itilizatè a
                print(f"Erè nan voye imèl: {e}")
            
            messages.success(request, 'Enskripsyon ou te soumèt avèk siksè!')
            return render(request, 'school_registration/enrollment_success.html', {
                'enrollment': enrollment,
                'document_upload_url': enrollment.get_document_upload_url(),
                'application_status_url': enrollment.get_application_status_url()
            })
    else:
        form = EnrollmentForm()
    
    context = {
        'form': form,
        'available_spots': available_spots,
        'today_registrations': today_registrations,
        'days_remaining': days_remaining,
    }
    
    return render(request, 'school_registration/enskripsyon-lekol-kreyol.html', context)

def document_upload_view(request, token):
    """
    View pou paj telechajman dokiman yo
    """
    # Jwenn enskripsyon an selon token an
    enrollment = get_object_or_404(Enrollment, access_token=token)
    
    # Jwenn dokiman ki deja telechaje yo
    existing_documents = Document.objects.filter(enrollment=enrollment)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.enrollment = enrollment
            document.save()
            
            messages.success(request, 'Dokiman an te telechaje avèk siksè!')
            
            # Mete ajou estati aplikasyon an si li te nan "DOCUMENTS_REQUIRED"
            if enrollment.status == 'documents_required' and existing_documents.count() > 0:
                enrollment.status = 'documents_received'
                enrollment.save()
            
            return redirect('document_upload', token=token)
    else:
        form = DocumentUploadForm()
    
    # Kreye yon lis dokiman ki obligatwa yo
    required_documents = [
        {'type': DocumentType.BIRTH_CERTIFICATE, 'uploaded': False},
        {'type': DocumentType.REPORT_CARD, 'uploaded': False},
        {'type': DocumentType.VACCINATION_CARD, 'uploaded': False},
        {'type': DocumentType.PASSPORT_PHOTO, 'uploaded': False},
        {'type': DocumentType.PROOF_OF_RESIDENCE, 'uploaded': False},
    ]
    
    # Si se lekòl segondè, ajoute lèt rekòmandasyon
    if enrollment.school_level == 'secondary':
        required_documents.append({'type': DocumentType.RECOMMENDATION_LETTER, 'uploaded': False})
    
    # Tcheke ki dokiman ki deja telechaje
    for doc in existing_documents:
        for req_doc in required_documents:
            if req_doc['type'] == doc.document_type:
                req_doc['uploaded'] = True
                req_doc['document'] = doc
    
    context = {
        'enrollment': enrollment,
        'form': form,
        'existing_documents': existing_documents,
        'required_documents': required_documents,
    }
    
    return render(request, 'school_registration/document_upload.html', context)

def delete_document_view(request, token, document_id):
    """
    View pou efase yon dokiman
    """
    # Jwenn enskripsyon an selon token an
    enrollment = get_object_or_404(Enrollment, access_token=token)
    
    # Jwenn dokiman an
    document = get_object_or_404(Document, id=document_id, enrollment=enrollment)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Dokiman an te efase avèk siksè!')
        
        # Mete ajou estati aplikasyon an si li te nan "DOCUMENTS_RECEIVED"
        remaining_docs = Document.objects.filter(enrollment=enrollment).count()
        if enrollment.status == 'documents_received' and remaining_docs == 0:
            enrollment.status = 'documents_required'
            enrollment.save()
    
    return redirect('document_upload', token=token)

def application_status_view(request, token):
    """
    View pou verifye estati aplikasyon an
    """
    # Jwenn enskripsyon an selon token an
    enrollment = get_object_or_404(Enrollment, access_token=token)
    
    # Jwenn dokiman ki deja telechaje yo
    documents = Document.objects.filter(enrollment=enrollment)
    
    # Kalkile pwogrè aplikasyon an
    progress = 0
    if enrollment.status == 'documents_required':
        progress = 10
    elif enrollment.status == 'documents_received':
        progress = 30
    elif enrollment.status == 'under_review':
        progress = 50
    elif enrollment.status == 'interview_scheduled':
        progress = 70
    elif enrollment.status in ['accepted', 'rejected', 'waitlisted']:
        progress = 100
    
    context = {
        'enrollment': enrollment,
        'documents': documents,
        'progress': progress,
        'document_upload_url': enrollment.get_document_upload_url(),
    }
    
    return render(request, 'school_registration/application_status.html', context)

def high_school_view(request):
    """
    View pou paj enfòmasyon sou lekòl segondè
    """
    return render(request, 'school_registration/lekol-segonde-kreyol.html')