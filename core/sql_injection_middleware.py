import re
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger('django.security')

class SqlInjectionProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Padrões comuns de SQL Injection
        self.sql_patterns = [
            r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
            r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
            r'((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))',
            r'((\%27)|(\'))union',
            r'exec(\s|\+)+(s|x)p\w+',
            r'insert(\s|\+)+into(\s|\+)+\w+',
            r'select(\s|\+)+[\[\]a-zA-Z0-9_\-\.,]+(\s|\+)+from',
            r'drop(\s|\+)+table',
            r'drop(\s|\+)+database',
            r'delete(\s|\+)+from',
            r'update(\s|\+)+\w+(\s|\+)+set',
            r'create(\s|\+)+table'
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]

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
                            f"Possível tentativa de SQL Injection detectada de {ip} para {request.path}: {key}={value}"
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
                            description=f"Possível SQL Injection: {key}={value}"
                        )
                        
                        return HttpResponseForbidden("Acesso negado: parâmetros inválidos.")
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip