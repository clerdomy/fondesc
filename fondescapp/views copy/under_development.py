from django.shortcuts import render


def under_development(request):
    """Render the under development page"""
    return render(request, 'fondescapp/site_under_development.html')
