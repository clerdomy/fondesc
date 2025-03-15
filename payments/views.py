import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

from .models import Payment, Invoice
from courses.models import Enrollment, Course

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY



@login_required
def payment_process_view(request, course_id):
    """View para exibir a página de processamento de pagamento"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verificar se o usuário já está inscrito
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, "Você já está inscrito neste curso.")
        return redirect('course_learn', slug=course.slug)
    
    # Calcular valores para exibição
    discount = 0
    tax = 1  # 10% de imposto (exemplo)
    total = course.price + tax - discount
    
    # Data para amanhã (para o campo de data no pagamento em dinheiro)
    tomorrow_date = timezone.now() + timedelta(days=1)
    
    context = {
        'course': course,
        'discount': discount,
        'tax': tax,
        'total': total,
        'tomorrow_date': tomorrow_date,
    }
    
    return render(request, 'payments/payment_process.html', context)

@login_required
def process_payment(request):
    """View para processar o pagamento submetido"""
    if request.method != 'POST':
        messages.error(request, "Método inválido.")
        return redirect('course_list')
    
    # Obter o curso
    course_id = request.POST.get('course_id')
    if not course_id:
        messages.error(request, "Curso não especificado.")
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Obter o método de pagamento
    payment_method = request.POST.get('payment_method')
    if not payment_method:
        messages.error(request, "Por favor, selecione um método de pagamento.")
        return redirect('payment_process', course_id=course_id)
    
    # Processar o pagamento (simulação)
    # Em um ambiente real, você integraria com gateways de pagamento aqui
    
    # Criar a inscrição
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_paid': False}  # Inicialmente marcado como não pago
    )
    
    # Atualizar status de pagamento com base no método
    if payment_method in ['card', 'moncash', 'lajancash']:
        # Métodos de pagamento instantâneos
        enrollment.is_paid = True
        enrollment.save()
        messages.success(request, f"Pagamento processado com sucesso! Você agora está inscrito em {course.title}.")
        return redirect('course_learn', slug=course.slug)
    else:
        # Métodos que requerem verificação manual
        messages.success(request, "Sua solicitação de inscrição foi recebida. Você receberá acesso ao curso assim que o pagamento for confirmado.")
        return redirect('dashboard')



@login_required
def payment_success(request, enrollment_id):
    """Handle successful payment"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    # Update enrollment status
    enrollment.is_paid = True
    enrollment.save()
    
    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        enrollment=enrollment,
        amount=enrollment.course.price,
        status='completed',
        payment_method='credit_card',
    )
    
    # Create invoice
    from datetime import datetime, timedelta
    invoice_number = f"INV-{payment.id}-{datetime.now().strftime('%Y%m%d')}"
    Invoice.objects.create(
        payment=payment,
        invoice_number=invoice_number,
        due_date=datetime.now().date() + timedelta(days=30),
    )
    
    messages.success(request, f"Payment successful! You are now enrolled in {enrollment.course.title}")
    return redirect('course_learn', slug=enrollment.course.slug)

@login_required
def payment_cancel(request, enrollment_id):
    """Handle cancelled payment"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    messages.warning(request, "Payment was cancelled. You can try again later.")
    return redirect('course_detail', slug=enrollment.course.slug)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get enrollment from client_reference_id
        enrollment_id = session.get('client_reference_id')
        if enrollment_id:
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id)
                
                # Update enrollment status
                enrollment.is_paid = True
                enrollment.save()
                
                # Create payment record
                payment = Payment.objects.create(
                    user=enrollment.user,
                    enrollment=enrollment,
                    amount=enrollment.course.price,
                    status='completed',
                    payment_method='credit_card',
                    transaction_id=session.get('payment_intent'),
                )
                
                # Create invoice
                from datetime import datetime, timedelta
                invoice_number = f"INV-{payment.id}-{datetime.now().strftime('%Y%m%d')}"
                Invoice.objects.create(
                    payment=payment,
                    invoice_number=invoice_number,
                    due_date=datetime.now().date() + timedelta(days=30),
                )
            except Enrollment.DoesNotExist:
                return HttpResponse(status=404)
    
    return HttpResponse(status=200)
