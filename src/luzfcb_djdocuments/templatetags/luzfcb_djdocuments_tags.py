# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import bleach
from django import template
from django.forms.models import modelform_factory
from django.utils.safestring import mark_safe
from django.template.defaultfilters import striptags

from simple_history.forms import new_readonly_form_class

from ..utils import identificador, split_utils

register = template.Library()


@register.filter
def as_form(model_instance):
    model = model_instance.__class__
    new_form_class = modelform_factory(model, fields='__all__')
    readonly_new_form_class = new_readonly_form_class(new_form_class)
    form_instance = readonly_new_form_class(instance=model_instance)

    return form_instance


@register.filter
def as_form_media(model_instance):
    model = model_instance.__class__
    new_form_class = modelform_factory(model, fields='__all__')
    readonly_new_form_class = new_readonly_form_class(new_form_class)
    form_instance = readonly_new_form_class(instance=model_instance)

    return form_instance.media


@register.filter
def identificador_versao(model_instance):
    if model_instance:
        return identificador.document(model_instance.pk, model_instance.versao_numero)


@register.filter
def dividir_a_cada(string, step=5, char=' - '):
    return split_utils.insert_char_each(string=string, char=char, step=step)


@register.filter
def absolute_uri(url, request):
    """
    Usage: {{ url|absolute_uri:request }}

    sample 1:

    {% url 'my-view' as my_view %}
    {{ my_view:absolute_uri:request }}

    <a href="{{ my_view|absolute_uri:request }}"></a>

    or

    {{ my_view|absolute_uri:request|urlize }}

    sample 2:

    {{ '/foo/bar/'|absolute_uri:request as zz }}
    """
    return request.build_absolute_uri(url)


@register.filter
def remover_tags_html(value):
    """
        Usage: {{ value|remover_tags_html }}
    """
    striped_str = striptags(value)
    return mark_safe(bleach.clean(striped_str))
