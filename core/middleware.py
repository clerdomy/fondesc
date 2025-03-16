from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseForbidden

# Lista de navegadores permitidos
ALLOWED_BROWSERS = ["chrome", "firefox", "safari", "edge"]

class BrowserRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

        # Verifica se o navegador está na lista de permitidos
        if not any(browser in user_agent for browser in ALLOWED_BROWSERS):
            return HttpResponseForbidden("Acesso negado: use Chrome, Firefox, Edge ou Safari.")

        response = self.get_response(request)
        return response


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is enabled
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access even in maintenance mode
            if not request.path.startswith('/admin/'):
                # Show the maintenance page
                context = {}
                return render(request, 'maintenance.html', context)
        
        # Continue with normal request processing
        response = self.get_response(request)
        return response

