from django.contrib import messages
from django.shortcuts import  render, redirect
from django.views.decorators.http import require_POST

from fondescapp.models import ContactMessage

def contact(request):
    return render(request, 'fondescapp/contact.html')


@require_POST
def contact_submit(request):
    """Handle contact form submission"""
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    privacy_agree = request.POST.get('privacy_agree', '') == 'on'
    
    # Validate required fields
    if not all([first_name, last_name, email, subject, message, privacy_agree]):
        messages.error(request, 'Tanpri ranpli tout chan obligatwa yo.')
        return redirect('contact_page')
    
    try:
        # Save the contact message to the database
        ContactMessage.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            privacy_agree=privacy_agree
        )
        
        # Send notification email to admin (optional)
        # send_admin_notification(first_name, last_name, email, subject, message)
        
        messages.success(request, 'Mèsi pou mesaj ou a! Nou pral kontakte ou byento.')
    except Exception as e:
        messages.error(request, 'Te gen yon erè. Tanpri eseye ankò.')
    
    return redirect('contact_page')

