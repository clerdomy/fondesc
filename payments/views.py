from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
from django.db import transaction

from courses.models import Course, Enrollment
from .models import Payment, Discount, PaymentNotification

import json
import uuid
import logging
import stripe
from datetime import timedelta
import decimal

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

@login_required
def payment_process_view(request, course_id):
    """View to display the payment processing page"""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is already enrolled
    if Enrollment.objects.filter(user=request.user, course=course, is_paid=True).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_learn', slug=course.slug)
    
    # Get discount code from session or request
    discount_code = request.session.get('discount_code') or request.GET.get('discount')
    discount_amount = 0
    discount_obj = None
    
    if discount_code:
        try:
            discount_obj = Discount.objects.get(code=discount_code)
            if discount_obj.is_valid:
                # Check if discount applies to this course
                if not discount_obj.courses.exists() or discount_obj.courses.filter(id=course.id).exists():
                    discount_amount = discount_obj.calculate_discount(course.price)
                    # Store discount code in session
                    request.session['discount_code'] = discount_code
                else:
                    messages.warning(request, "This discount code is not valid for this course.")
                    discount_obj = None
                    if 'discount_code' in request.session:
                        del request.session['discount_code']
            else:
                messages.warning(request, "This discount code is no longer valid.")
                discount_obj = None
                if 'discount_code' in request.session:
                    del request.session['discount_code']
        except Discount.DoesNotExist:
            messages.warning(request, "Invalid discount code.")
            if 'discount_code' in request.session:
                del request.session['discount_code']
    
    # Calculate values for display
    tax = int(course.price * decimal.Decimal("0.10"))  # 10% tax (example)
    subtotal = course.price
    total = subtotal + tax - discount_amount
    
    # Date for tomorrow (for cash payment date field)
    tomorrow_date = timezone.now() + timedelta(days=1)
    
    context = {
        'course': course,
        'discount': discount_amount,
        'discount_obj': discount_obj,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'tomorrow_date': tomorrow_date,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    
    return render(request, 'payments/payment_process.html', context)

@login_required
def apply_discount(request):
    """AJAX view to apply a discount code"""
    if request.method == 'POST':
        code = request.POST.get('code')
        course_id = request.POST.get('course_id')
        
        if not code or not course_id:
            return JsonResponse({'success': False, 'message': 'Missing required parameters'})
        
        try:
            course = Course.objects.get(id=course_id)
            discount = Discount.objects.get(code=code)
            
            if not discount.is_valid:
                return JsonResponse({'success': False, 'message': 'This discount code is no longer valid'})
            
            # Check if discount applies to this course
            if discount.courses.exists() and not discount.courses.filter(id=course.id).exists():
                return JsonResponse({'success': False, 'message': 'This discount code is not valid for this course'})
            
            discount_amount = discount.calculate_discount(course.price)
            
            # Store discount code in session
            request.session['discount_code'] = code
            
            # Calculate new total
            tax = course.price * 0.10  # 10% tax (example)
            subtotal = course.price
            total = subtotal + tax - discount_amount
            
            return JsonResponse({
                'success': True,
                'message': 'Discount applied successfully',
                'discount_amount': float(discount_amount),
                'new_total': float(total),
                'discount_info': {
                    'code': discount.code,
                    'description': discount.description
                }
            })
            
        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Course not found'})
        except Discount.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid discount code'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@transaction.atomic
def process_payment(request):
    """View to process the submitted payment"""
    if request.method != 'POST':
        messages.error(request, "Invalid method.")
        return redirect('course_list')
    
    # Get the course
    course_id = request.POST.get('course_id')
    if not course_id:
        messages.error(request, "Course not specified.")
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Get the payment method
    payment_method = request.POST.get('payment_method')
    if not payment_method:
        messages.error(request, "Please select a payment method.")
        return redirect('payment_process', course_id=course_id)
    
    # Calculate payment amount
    discount_code = request.session.get('discount_code')
    discount_amount = 0
    
    if discount_code:
        try:
            discount = Discount.objects.get(code=discount_code)
            if discount.is_valid:
                # Check if discount applies to this course
                if not discount.courses.exists() or discount.courses.filter(id=course.id).exists():
                    discount_amount = discount.calculate_discount(course.price)
                    # Increment discount usage
                    discount.current_uses += 1
                    discount.save()
        except Discount.DoesNotExist:
            pass
    
    tax = int(course.price * decimal.Decimal("0.10"))  # 10% tax (example)
    total = course.price + tax - discount_amount
    
    # Create payment record
    payment = Payment(
        user=request.user,
        course=course,
        amount=total,
        currency='HTG',
        payment_method=payment_method,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    # Process payment based on method
    if payment_method == 'card':
        # Get Stripe payment intent ID
        payment_intent_id = request.POST.get('payment_intent_id')
        if not payment_intent_id:
            messages.error(request, "Payment processing error. Please try again.")
            return redirect('payment_process', course_id=course_id)
        
        try:
            # Retrieve the payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Verify the payment intent
            if intent.status == 'succeeded':
                # Payment was successful
                payment.status = 'completed'
                payment.transaction_id = intent.id
                payment.stripe_payment_intent_id = intent.id
                payment.stripe_payment_method_id = intent.payment_method
                payment.save()
                
                # Create enrollment (this happens automatically in the save method)
                messages.success(request, f"Payment processed successfully! You are now enrolled in {course.title}.")
                return redirect('course_learn', slug=course.slug)
            else:
                # Payment failed or is still processing
                payment.status = 'failed' if intent.status == 'canceled' else 'processing'
                payment.transaction_id = intent.id
                payment.stripe_payment_intent_id = intent.id
                payment.stripe_payment_method_id = intent.payment_method
                payment.save()
                
                if intent.status == 'processing':
                    messages.info(request, "Your payment is still processing. You will be enrolled once the payment is confirmed.")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Payment failed. Please try again or choose a different payment method.")
                    return redirect('payment_process', course_id=course_id)
                
        except stripe.error.StripeError as e:
            # Log the error
            logger.error(f"Stripe error: {str(e)}")
            
            # Save the failed payment
            payment.status = 'failed'
            payment.notes = f"Stripe error: {str(e)}"
            payment.save()
            
            messages.error(request, "Payment processing error. Please try again or contact support.")
            return redirect('payment_process', course_id=course_id)
    
    elif payment_method == 'moncash':
        phone_number = request.POST.get('moncash_phone')
        if not phone_number:
            messages.error(request, "Please provide your MonCash phone number.")
            return redirect('payment_process', course_id=course_id)
        
        payment.phone_number = phone_number
        payment.status = 'pending'  # Changed from 'processing' to 'pending'
        payment.save()
        
        # Here you would integrate with MonCash API
        # For now, we'll just create a pending payment that requires manual verification
        
        messages.success(request, "Your payment information has been received. Your enrollment will be activated once the payment is verified.")
        return redirect('payment_confirmation', payment_id=payment.id)
    
    elif payment_method == 'lajancash':
        phone_number = request.POST.get('lajancash_phone')
        if not phone_number:
            messages.error(request, "Please provide your Lajan Cash phone number.")
            return redirect('payment_process', course_id=course_id)
        
        payment.phone_number = phone_number
        payment.status = 'pending'  # Changed from 'processing' to 'pending'
        payment.save()
        
        # Here you would integrate with Lajan Cash API
        # For now, we'll just create a pending payment that requires manual verification
        
        messages.success(request, "Your payment information has been received. Your enrollment will be activated once the payment is verified.")
        return redirect('payment_confirmation', payment_id=payment.id)
    
    elif payment_method == 'bank':
        bank_reference = request.POST.get('bank_reference')
        payment.bank_reference = bank_reference
        payment.status = 'pending'
        payment.save()
        
        # Handle receipt file upload
        if 'bank_receipt' in request.FILES:
            payment.receipt_file = request.FILES['bank_receipt']
            payment.save()
        
        messages.success(request, "Your bank transfer information has been received. Your enrollment will be activated once the payment is verified.")
        return redirect('payment_confirmation', payment_id=payment.id)
    
    elif payment_method == 'remittance':
        remittance_service = request.POST.get('remittance_service')
        remittance_sender = request.POST.get('remittance_sender')
        remittance_mtcn = request.POST.get('remittance_mtcn')
        remittance_amount = request.POST.get('remittance_amount')
        remittance_currency = request.POST.get('remittance_currency')
        
        if not all([remittance_service, remittance_sender, remittance_mtcn, remittance_amount, remittance_currency]):
            messages.error(request, "Please provide all required remittance information.")
            return redirect('payment_process', course_id=course_id)
        
        payment.remittance_info = {
            'service': remittance_service,
            'sender': remittance_sender,
            'mtcn': remittance_mtcn,
            'amount': remittance_amount,
            'currency': remittance_currency
        }
        payment.status = 'pending'
        payment.save()
        
        messages.success(request, "Your remittance information has been received. Your enrollment will be activated once the payment is verified.")
        return redirect('payment_confirmation', payment_id=payment.id)
    
    elif payment_method == 'cash':
        cash_location = request.POST.get('cash_location')
        cash_date = request.POST.get('cash_date')
        
        payment.notes = f"Cash payment at {cash_location} on {cash_date}"
        payment.status = 'pending'
        payment.save()
        
        messages.success(request, "Your cash payment reservation has been received. Please visit our office to complete the payment.")
        return redirect('payment_confirmation', payment_id=payment.id)
    
    else:
        messages.error(request, "Invalid payment method.")
        return redirect('payment_process', course_id=course_id)

@login_required
def create_payment_intent(request):
    """AJAX view to create a Stripe payment intent"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        course_id = data.get('course_id')
        
        if not course_id:
            return JsonResponse({'error': 'Course ID is required'}, status=400)
        
        course = get_object_or_404(Course, id=course_id)
        
        # Calculate payment amount
        discount_code = request.session.get('discount_code')
        discount_amount = 0
        
        if discount_code:
            try:
                discount = Discount.objects.get(code=discount_code)
                if discount.is_valid:
                    # Check if discount applies to this course
                    if not discount.courses.exists() or discount.courses.filter(id=course.id).exists():
                        discount_amount = discount.calculate_discount(course.price)
            except Discount.DoesNotExist:
                pass
        
        tax = course.price * 0.10  # 10% tax (example)
        total = course.price + tax - discount_amount
        
        # Convert to cents for Stripe
        amount_in_cents = int(total * 100)
        
        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd',  # Change to your currency
            metadata={
                'course_id': course.id,
                'user_id': request.user.id,
                'course_title': course.title
            }
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
        
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@login_required
def payment_confirmation(request, payment_id):
    """View to display payment confirmation"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/payment_confirmation.html', context)

@login_required
def payment_history(request):
    """View to display user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/payment_history.html', context)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Webhook endpoint for Stripe events"""
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
    
    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        
        # Find the payment
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
             
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
            
            # Update payment status if it's not already completed
            if payment.status != 'completed':
                payment.status = 'completed'
                payment.save()
                
                # Log the webhook event
                PaymentNotification.objects.create(
                    payment=payment,
                    notification_type='stripe_webhook',
                    notification_data=event.data.object
                )
                
                # Send confirmation email to user
                # This would be implemented in a real application
                
        except Payment.DoesNotExist:
            # Payment not found, log this for investigation
            logger.error(f"Payment not found for Stripe PaymentIntent ID: {payment_intent.id}")
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
            payment.status = 'failed'
            payment.save()
            
            # Log the webhook event
            PaymentNotification.objects.create(
                payment=payment,
                notification_type='stripe_webhook',
                notification_data=event.data.object
            )
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for Stripe PaymentIntent ID: {payment_intent.id}")
    
    # Return a response to acknowledge receipt of the event
    return HttpResponse(status=200)

@csrf_exempt
@require_POST
def payment_webhook(request, provider):
    """Webhook endpoint for payment providers to send notifications"""
    if provider not in ['moncash', 'lajancash']:
        return HttpResponse(status=404)
    
    # Get the request body
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    
    # Verify the webhook signature (implementation depends on the provider)
    # This is a simplified example
    
    # Process the webhook based on the provider
    if provider == 'moncash':
        transaction_id = payload.get('transaction_id')
        status = payload.get('status')
        
        if not transaction_id or not status:
            return HttpResponse(status=400)
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return HttpResponse(status=404)
        
        # Store the notification
        PaymentNotification.objects.create(
            payment=payment,
            notification_type=f"{provider}_webhook",
            notification_data=payload
        )
        
        # Update payment status
        if status == 'success':
            payment.status = 'completed'
            payment.save()
        elif status == 'failed':
            payment.status = 'failed'
            payment.save()
        
        return HttpResponse(status=200)
    
    # Similar implementations for other providers
    
    return HttpResponse(status=200)

