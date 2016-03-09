# -*- coding: utf-8 -*-
from django.apps import apps
from django.db import models
from django.utils import six

from ..exceptions import InvalidDotPathToModelException, NonDjangoModelSubclassException
from ..settings import USER_MODEL


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


def get_real_user_model_class():
    return get_real_model_class(USER_MODEL)
