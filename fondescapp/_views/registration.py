from django.shortcuts import render
from django.http import HttpResponse

from fondescapp.models import StudentProfile, MethodPayment, Document

def registration_view(request):
    if request.method == 'POST':
        # user information
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # student information
        phone = request.POST.get('phone')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        education_level = request.POST.get('education_level')

        course_type = request.POST.get('course_type')
        course = request.POST.get('course')

        start_date = request.POST.get('start_date')

        payment_option = request.POST.get('payment_option')
        payment_method = request.POST.get('payment_method')

        # credit or debit card details
        card_cvv = request.POST.get('card_cvv')
        card_expiry = request.POST.get('card_expiry')
        card_number = request.POST.get('card_number')
        card_name = request.POST.get('card_name')

        # get transfer details
        bank_receipt = request.POST.get('bank_receipt')

        # get mobile code
        mobile_code = request.POST.get('mobile_code')

        # Handle file uploads
        id_document = request.FILES.get('id_document')
        diploma = request.FILES.get('diploma')
        transcript = request.FILES.get('transcript')
        photo = request.FILES.get('photo')
        bank_receipt = request.FILES.get('bank_receipt')

        candidate = StudentProfile.objects.create(
            phone=phone,
            birth_date=birth_date,
            gender=gender,
            address=address,
            city=city,
            postal_code=postal_code,
            education_level=education_level, 
        )
        candidate.save()

        # create user
        candidate.create_user(
            email,
           first_name,
           last_name,
       )
        candidate.save()
        # Create the Payment object

        payment = MethodPayment.objects.create(
            student=candidate,
            payment_option=payment_option,
            payment_method= payment_method,
            terms_accepted=True,

            bank_receipt=bank_receipt,

            card_cvv=card_cvv,
            card_expiry=card_expiry,
            card_number=card_number,
            card_name=card_name,

            mobile_code=mobile_code,
        )
        # Create the Document object
        document = Document.objects.create(
            student=candidate,
            id_document=id_document,
            diploma=diploma,
            transcript=transcript,
            photo=photo,
        )
        document.save()



        # For now, just print the data
        print({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'birth_date': birth_date,
            'gender': gender,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'education_level': education_level,
            'course_type': course_type,
            'course': course,
            'start_date': start_date,
            'payment_option': payment_option,
            'payment_method': payment_method,
        })

        # Process files if uploaded
        if id_document:
            print(f"ID Document uploaded: {id_document.name}")
        if diploma:
            print(f"Diploma uploaded: {diploma.name}")
        if transcript:
            print(f"Transcript uploaded: {transcript.name}")
        if photo:
            print(f"Photo uploaded: {photo.name}")
        if bank_receipt:
            print(f"Bank Receipt uploaded: {bank_receipt.name}")

        # Redirect or return a success message
        return HttpResponse("Enskripsyon ou soumèt avèk siksè! Nou pral kontakte ou byento.")
    else:
        # If GET request, render the registration form
        return render(request, 'fondescapp/registration.html')
    