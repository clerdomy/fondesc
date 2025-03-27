from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger('django.security')

class EnhancedCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Verificar se a view está isenta de CSRF
        if getattr(callback, 'csrf_exempt', False):
            return None
        
        # Verificar se é uma requisição que precisa de CSRF
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            # Obter o token CSRF da requisição
            csrf_token = self._get_token(request)
            
            # Se não houver token CSRF, registrar e bloquear
            if csrf_token is None:
                ip = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                logger.warning(
                    f"Tentativa de requisição sem token CSRF de {ip} para {request.path}"
                )
                
                # Registrar evento de segurança se você estiver usando o modelo SecurityEvent
                from .security_monitoring import SecurityEvent
                SecurityEvent.objects.create(
                    event_type='csrf_failure',
                    severity='medium',
                    ip_address=ip,
                    user_agent=user_agent,
                    user=request.user if request.user.is_authenticated else None,
                    url=request.path,
                    description="Requisição sem token CSRF"
                )
                
                return HttpResponseForbidden("Erro de CSRF: token ausente ou inválido.")
        
        # Continuar com a verificação padrão de CSRF
        return super().process_view(request, callback, callback_args, callback_kwargs)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip