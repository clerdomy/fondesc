from django.db import models
from django.contrib.auth.signals import user_login_failed, user_logged_in, user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger('django.security')

# Modelo para registrar tentativas de login
class LoginAttempt(models.Model):
    username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['username']),
            models.Index(fields=['timestamp']),
        ]

# Modelo para registrar atividades suspeitas
class SecurityEvent(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    EVENT_TYPES = (
        ('auth_failure', 'Authentication Failure'),
        ('csrf_failure', 'CSRF Failure'),
        ('rate_limit', 'Rate Limit Exceeded'),
        ('permission_denied', 'Permission Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('other', 'Other'),
    )
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    url = models.TextField()
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
        ]

# Receivers para eventos de autenticação
@receiver(user_login_failed)
def log_login_failure(sender, credentials, **kwargs):
    username = credentials.get('username', 'unknown')
    request = kwargs.get('request')
    
    if request:
        ip = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Registrar no banco de dados
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip,
            user_agent=user_agent,
            successful=False
        )
        
        # Verificar tentativas repetidas
        recent_failures = LoginAttempt.objects.filter(
            username=username,
            ip_address=ip,
            successful=False,
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=10)
        ).count()
        
        if recent_failures >= 5:
            # Registrar evento de segurança
            SecurityEvent.objects.create(
                event_type='auth_failure',
                severity='medium' if recent_failures < 10 else 'high',
                ip_address=ip,
                user_agent=user_agent,
                url=request.path,
                description=f"Múltiplas falhas de login ({recent_failures}) para o usuário {username}"
            )
            
            logger.warning(
                f"Possível ataque de força bruta: {recent_failures} tentativas de login para {username} de {ip}"
            )

@receiver(user_logged_in)
def log_login_success(sender, request, user, **kwargs):
    if request:
        ip = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Registrar no banco de dados
        LoginAttempt.objects.create(
            username=user.username,
            ip_address=ip,
            user_agent=user_agent,
            successful=True
        )
        
        # Verificar login de local incomum
        unusual_location = check_unusual_location(user, ip)
        if unusual_location:
            SecurityEvent.objects.create(
                event_type='suspicious_activity',
                severity='medium',
                ip_address=ip,
                user_agent=user_agent,
                user=user,
                url=request.path,
                description=f"Login de localização incomum para o usuário {user.username}"
            )
            
            logger.warning(
                f"Login de localização incomum para {user.username} de {ip}"
            )

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_unusual_location(user, ip):
    # Implementar lógica para verificar se o IP é incomum para este usuário
    # Esta é uma implementação simplificada
    usual_ips = LoginAttempt.objects.filter(
        username=user.username,
        successful=True
    ).values_list('ip_address', flat=True).distinct()
    
    return ip not in usual_ips