import re
from django.http import HttpResponseForbidden
import logging
import html

logger = logging.getLogger('django.security')

class XssProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Padrões comuns de XSS
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript\s*:',
            r'onerror\s*=',
            r'onload\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'eval\s*\(',
            r'document\.cookie',
            r'document\.location',
            r'document\.write',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<base[^>]*>'
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]

    def __call__(self, request):
        # Verificar parâmetros GET e POST
        params = {}
        params.update(request.GET.items())
        params.update(request.POST.items())
        
        for key, value in params.items():
            if isinstance(value, str):
                for pattern in self.compiled_patterns:
                    if pattern.search(value):
                        ip = self._get_client_ip(request)
                        user_agent = request.META.get('HTTP_USER_AGENT', '')
                        
                        logger.warning(
                            f"Possível tentativa de XSS detectada de {ip} para {request.path}: {key}={html.escape(value)}"
                        )
                        
                        # Registrar evento de segurança
                        from .security_monitoring import SecurityEvent
                        SecurityEvent.objects.create(
                            event_type='suspicious_activity',
                            severity='high',
                            ip_address=ip,
                            user_agent=user_agent,
                            user=request.user if request.user.is_authenticated else None,
                            url=request.path,
                            description=f"Possível XSS: {key}={html.escape(value)}"
                        )
                        
                        return HttpResponseForbidden("Acesso negado: parâmetros inválidos.")
        
        response = self.get_response(request)
        
        # Adicionar cabeçalhos de segurança para XSS
        response['X-XSS-Protection'] = '1; mode=block'
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self';"
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip