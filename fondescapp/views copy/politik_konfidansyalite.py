from django.shortcuts import render

def politik_konfidansyalite_page(request):
    """Render the privacy policy page"""
    return render(request, 'fondescapp/politik-konfidansyalite.html')
