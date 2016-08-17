# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model

DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD = getattr(settings, 'DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD', False)
USER_MODEL = get_user_model

DOCUMENT_DEFAULT_BACKEND = {
    'BACKEND': 'luzfcb_djdocuments.backends.SolarDefensoriaBackend',
    'GRUPO_ASSINANTE_MODEL': 'contrib.Defensoria',
}

if not hasattr(settings, 'DJDOCUMENT'):
    setattr(settings, 'DJDOCUMENT', DOCUMENT_DEFAULT_BACKEND)

DJDOCUMENT = getattr(settings, 'DJDOCUMENT', None)
