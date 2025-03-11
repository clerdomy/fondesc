from django.shortcuts import render

def privacy_policy(request):
    """Render the privacy policy page"""
    return render(request, 'fondescapp/privacy_policy.html')
