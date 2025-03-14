from django.shortcuts import render

def home_view(request):
    """View for the home page"""
    return render(request, 'home.html')

def about_view(request):
    """View for the about page"""
    return render(request, 'about.html')

def contact_view(request):
    """View for the contact page"""
    return render(request, 'contact.html')