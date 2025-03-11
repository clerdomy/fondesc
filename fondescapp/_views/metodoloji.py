from django.shortcuts import render

def metodoloji_page(request):
    """Render the methodology page"""
    return render(request, 'fondescapp/metodoloji.html')

