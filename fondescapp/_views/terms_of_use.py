from django.shortcuts import render

def terms_of_use(request):
    """Render the terms of use page"""
    return render(request, 'fondescapp/terms_of_use.html')


