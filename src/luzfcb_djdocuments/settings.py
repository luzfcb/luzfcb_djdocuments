# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings

DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD = getattr(settings, 'DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD', False)
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
