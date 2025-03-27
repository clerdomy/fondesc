#!/bin/bash

# Atualizar o sistema
apt update && apt upgrade -y

# Instalar ferramentas de segurança
apt install -y fail2ban ufw unattended-upgrades logwatch rkhunter

# Configurar firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable

# Configurar fail2ban para proteger SSH e outros serviços
cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
EOF

# Reiniciar fail2ban
systemctl restart fail2ban

# Configurar atualizações automáticas
cat > /etc/apt/apt.conf.d/20auto-upgrades << EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

# Endurecer configurações SSH
cat > /etc/ssh/sshd_config.d/hardening.conf << EOF
PermitRootLogin no
PasswordAuthentication no
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers seu_usuario
Protocol 2
EOF

# Reiniciar SSH
systemctl restart sshd

# Configurar limites de recursos do sistema
cat >> /etc/security/limits.conf << EOF
* soft nofile 65535
* hard nofile 65535
www-data soft nproc 1024
www-data hard nproc 2048
EOF

# Configurar proteções de kernel
cat > /etc/sysctl.d/99-security.conf << EOF
# Proteção contra ataques de IP spoofing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Desabilitar redirecionamentos ICMP
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Desabilitar source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Habilitar proteção contra-ataques SYN flood
net.ipv4.tcp_syncookies = 1

# Habilitar proteção contra-ataques de tempo
net.ipv4.tcp_timestamps = 0

# Aumentar o range de portas efêmeras
net.ipv4.ip_local_port_range = 1024 65535

# Aumentar o tamanho da fila de backlog
net.core.somaxconn = 4096
EOF

# Aplicar configurações de kernel
sysctl -p /etc/sysctl.d/99-security.conf

# Configurar auditoria de segurança
apt install -y auditd
systemctl enable auditd
systemctl start auditd

# Configurar regras de auditoria básicas
cat > /etc/audit/rules.d/audit.rules << EOF
# Monitorar alterações em arquivos de configuração
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k identity
-w /etc/ssh/sshd_config -p wa -k sshd_config

# Monitorar comandos sudo
-w /usr/bin/sudo -p x -k sudo_log

# Monitorar alterações em arquivos do Django
-w /home/ubuntu/projects/fondesc/ -p wa -k django_files
EOF

# Reiniciar auditd
systemctl restart auditd

echo "Hardening do servidor concluído!"
