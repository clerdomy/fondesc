from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST


from fondescapp.models import ScholarshipInterest



def scholarships_page(request):
    """Render the scholarships page"""
    return render(request, 'fondescapp/scholarships.html')


@require_POST
def scholarship_interest(request):
    """Handle scholarship interest form submission"""
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    scholarship_type = request.POST.get('scholarship_type', '')
    education_level = request.POST.get('education_level', '')
    program_interest = request.POST.get('program_interest', '')
    comments = request.POST.get('comments', '')
    privacy_agree = request.POST.get('privacy_agree', '') == 'on'
    
    # Validate required fields
    if not all([first_name, last_name, email, scholarship_type, education_level, program_interest, privacy_agree]):
        messages.error(request, 'Tanpri ranpli tout chan obligatwa yo.')
        return redirect('scholarships_page')
    
    try:
        # Save the scholarship interest to the database
        ScholarshipInterest.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            scholarship_type=scholarship_type,
            education_level=education_level,
            program_interest=program_interest,
            comments=comments,
            privacy_agree=privacy_agree
        )
        
        # Send notification email to admin (optional)
        # send_admin_notification(first_name, last_name, email, scholarship_type)
        
        messages.success(request, 'Mèsi pou enterè ou nan bous detid nou yo! Nou pral kontakte ou byento ak plis enfòmasyon.')
    except Exception as e:
        messages.error(request, 'Te gen yon erè. Tanpri eseye ankò.')
    
    return redirect('scholarships_page')
