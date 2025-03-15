from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.urls import reverse
from django.utils.crypto import get_random_string
from .models import Contact, NewsletterSubscriber
from courses.models import Course



# Adicione ou atualize a função de visualização da página inicial
def home_view(request):
    """Home page view"""
    # Obter cursos em destaque (por exemplo, os 3 mais recentes)
    featured_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    context = {
        'featured_courses': featured_courses,
    }
    return render(request, 'home.html', context)

def about_view(request):
    """View for the about page"""
    return render(request, 'about.html')

def cookie_policy_view(request):
    return render(request, 'cookie_policy.html') 

def privacy_policy_view(request):
    """View for the privacy policy page"""
    return render(request, 'privacy_policy.html')

def terms_of_service_view(request):
    """View for the terms of service page"""
    return render(request, 'terms_of_service.html')

def contact_view(request):
    """View for handling contact form submissions"""
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Validate form data
        if not all([name, email, subject, message]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'contact.html')
        
        # Save contact to database
        try:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                ip_address=get_client_ip(request)
            )
            
            # Get the display value of the subject choice
            subject_display = contact.get_subject_display()
            
            # Prepare email subject
            subject_prefix = {
                'general': '[Informações Gerais]',
                'courses': '[Dúvidas sobre Cursos]',
                'technical': '[Suporte Técnico]',
                'billing': '[Pagamentos]',
                'partnership': '[Parcerias]',
                'other': '[Outro Assunto]'
            }.get(subject, '[Contato Website]')
            
            email_subject = f"{subject_prefix} Nova mensagem de {name}"
            
            # Prepare context for email templates
            current_date = timezone.now().strftime('%d/%m/%Y %H:%M')
            admin_url = request.build_absolute_uri(
                reverse('admin:fondescapp_contact_change', args=[contact.pk])
            )
            
            context = {
                'name': name,
                'email': email,
                'phone': phone,
                'subject': email_subject,
                'subject_display': subject_display,
                'message': message,
                'date': current_date,
                'admin_url': admin_url
            }
            
            # Send notification email to admin
            send_html_email(
                email_subject,
                'emails/contact_notification.html',
                context,
                [settings.CONTACT_EMAIL]
            )
            
            # Send confirmation email to user
            confirmation_subject = "Recebemos sua mensagem - PythonLearn"
            send_html_email(
                confirmation_subject,
                'emails/contact_confirmation.html',
                context,
                [email]
            )
            
            # Show success message
            messages.success(request, 'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.')
            
            # Redirect to a fresh form
            return render(request, 'contact.html')
            
        except Exception as e:
            # Log the error (in a production environment)
            print(f"Error processing contact form: {e}")
            messages.error(request, 'Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.')
    
    # For GET requests, just render the contact form
    return render(request, 'contact.html')

def send_html_email(subject, template_name, context, recipient_list):
    """Helper function to send HTML emails"""
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def newsletter_subscribe(request):
    """View for handling newsletter subscriptions"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        
        # Validate email
        if not email:
            messages.error(request, 'Por favor, informe seu email para se inscrever na newsletter.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        try:
            # Check if already subscribed
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'ip_address': get_client_ip(request),
                    'confirmation_token': get_random_string(64)
                }
            )
            
            if created:
                # Send confirmation email
                confirmation_url = request.build_absolute_uri(
                    reverse('newsletter_confirm', args=[subscriber.confirmation_token])
                )
                
                context = {
                    'name': name or 'Subscriber',
                    'confirmation_url': confirmation_url,
                    'current_year': timezone.now().year
                }
                
                send_html_email(
                    'Confirme sua inscrição na newsletter - Fondesc',
                    'emails/newsletter_confirmation.html',
                    context,
                    [email]
                )
                
                messages.success(request, 'Obrigado por se inscrever! Por favor, verifique seu email para confirmar sua inscrição.')
            else:
                # Already subscribed
                if subscriber.is_active:
                    messages.info(request, 'Você já está inscrito em nossa newsletter.')
                else:
                    # Reactivate subscription
                    subscriber.is_active = True
                    subscriber.save(update_fields=['is_active', 'updated_at'])
                    messages.success(request, 'Sua inscrição na newsletter foi reativada com sucesso!')
        
        except Exception as e:
            # Log the error
            print(f"Error processing newsletter subscription: {e}")
            messages.error(request, 'Ocorreu um erro ao processar sua inscrição. Por favor, tente novamente mais tarde.')
        
        # Redirect back to the referring page
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # If not POST, redirect to home
    return redirect('home')

def newsletter_confirm(request, token):
    """View for confirming newsletter subscriptions"""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
        
        if not subscriber.confirmed_at:
            subscriber.confirm_subscription()
            messages.success(request, 'Sua inscrição na newsletter foi confirmada com sucesso! Obrigado por se inscrever.')
        else:
            messages.info(request, 'Sua inscrição já foi confirmada anteriormente.')
        
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'Link de confirmação inválido ou expirado.')
    
    return redirect('home')

def newsletter_unsubscribe(request, email):
    """View for unsubscribing from the newsletter"""
    try:
        subscriber = NewsletterSubscriber.objects.get(email=email)
        subscriber.unsubscribe()
        messages.success(request, 'Você foi removido da nossa lista de newsletter com sucesso.')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'Email não encontrado em nossa lista de newsletter.')
    
    return redirect('home')

def send_html_email(subject, template_name, context, recipient_list):
    """Helper function to send HTML emails"""
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    email.send()




