#!/usr/bin/env python
import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar o modelo User
from accounts.models import User

# Importar e executar o comando
for i in range(10):
    username = f'testuser{i}'
    email = f'testuser{i}@example.com'
    password = 'testpassword'
    user = User.objects.create_user(username=username, email=email, password=password)
  