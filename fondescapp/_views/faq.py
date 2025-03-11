from django.shortcuts import render

def faq_page(request):
    """Render the FAQ page"""
    return render(request, 'fondescapp/faq.html')
