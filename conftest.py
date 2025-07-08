import os
import django
from django.core.management import call_command

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.test')
    django.setup()
    call_command('migrate', run_syncdb=True, verbosity=0)
