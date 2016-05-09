"""
WSGI config for test_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, 'tests'))
sys.path.append(os.path.join(BASE_DIR, 'src'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


application = get_wsgi_application()
application = DjangoWhiteNoise(application)
