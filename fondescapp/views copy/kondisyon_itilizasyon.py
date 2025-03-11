from django.shortcuts import render

def kondisyon_itilizasyon_page(request):
    """Render the terms of use page"""
    return render(request, 'fondescapp/kondisyon-itilizasyon.html')


