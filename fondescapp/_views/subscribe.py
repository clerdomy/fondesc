from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
def subscribe(request):
    """Handle email subscription for launch notification"""
    email = request.POST.get('email', '')
    
    if not email:
        messages.error(request, 'Tanpri antre yon adrès imèl valid.')
        return redirect('under_development')
    
    try:
        # Save the email to your database or newsletter service
        # This is a placeholder - implement your actual subscription logic
        # For example:
        # Subscriber.objects.create(email=email)
        
        messages.success(request, 'Mèsi! Nou pral fè w konnen lè sit la lanse.')
    except Exception as e:
        messages.error(request, 'Te gen yon erè. Tanpri eseye ankò.')
    
    return redirect('under_development')

