"""
WSGI config for motor_freelance project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motor_freelance.settings')

application = get_wsgi_application()
