#!/usr/bin/env python
import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar e executar o comando
from django.core.management import call_command
call_command('create_test_courses')

