import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment, Invoice
from courses.models import Enrollment, Course

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_process(request, enrollment_id):
    """Process payment for course enrollment"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    course = enrollment.course
    
    # Check if already paid
    if enrollment.is_paid:
        messages.info(request, f"You have already paid for {course.title}")
        return redirect('course_learn', slug=course.slug)
    
    if request.method == 'POST':
        # Create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': course.title,
                                'description': course.short_description,
                            },
                            'unit_amount': int(course.price * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('payment_success', args=[enrollment.id])
                ),
                cancel_url=request.build_absolute_uri(
                    reverse('payment_cancel', args=[enrollment.id])
                ),
                client_reference_id=str(enrollment.id),
                customer_email=request.user.email,
            )
            
            # Redirect to Stripe Checkout
            return redirect(checkout_session.url)
        
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('course_detail', slug=course.slug)
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    
    return render(request, 'payments/payment_process.html', context)

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
