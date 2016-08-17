# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.apps import apps
from django.db import models
from django.utils import six

from ..exceptions import InvalidDotPathToModelException, NonDjangoModelSubclassException


def get_real_model_class(klass_or_str):
    """
    Return real django model class definition from string in format 'app_name.ModelName'
    :param klass_or_str:
    :return: real class
    """
    if isinstance(klass_or_str, six.string_types):
        parts = klass_or_str.split('.')
        if len(parts) == 2:
            # if 'app_name.ModelName'
            app_label = parts[0]
            model_name = parts[-1]
            model = apps.get_model(app_label=app_label, model_name=model_name)
            return model
        else:
            raise InvalidDotPathToModelException(klass_or_str)
    if issubclass(klass_or_str, models.Model):
        return klass_or_str
    else:
        raise NonDjangoModelSubclassException(klass_or_str)


def import_member(import_string):
    """Import one member of Python module by path.
    >>> import os.path
    >>> imported = import_member('os.path.supports_unicode_filenames')
    >>> os.path.supports_unicode_filenames is imported
    True
    """
    module_name, factory_name = str(import_string).rsplit('.', 1)
    module = __import__(module_name, globals(), locals(), [factory_name], 0)
    return getattr(module, factory_name)
