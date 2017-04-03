# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import bleach
from django import template
from django.forms.models import modelform_factory
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from simple_history.forms import new_readonly_form_class

from ..utils import identificador, split_utils, get_djdocuments_backend

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
def dividir_a_cada(string, step=5, char='-'):
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


@register.inclusion_tag('luzfcb_djdocuments/templatetags/assinatura_a_element.html', takes_context=True,
                        name='register_assinatura_pendente_to_modal')
def register_assinatura_pendente_to_modal(context, assinatura_object, context_name,
                                          template='luzfcb_djdocuments/templatetags/assinatura_a_element.html'):
    foobar = []
    ctx_name = 'djdocs_global'
    assinatura = None
    try:
        # foobar = context['to_modal_assinatura_pendente']
        ctx_name = 'djdocs_{}'.format(context_name)
        foobar = context[ctx_name]
    except KeyError:
        pass
    if assinatura_object and not assinatura_object.esta_assinado:
        foobar.append(assinatura_object)
        assinatura = assinatura_object
    context.dicts[0][ctx_name] = foobar
    template_context = {
        'template': template,
        'assinatura': assinatura

    }
    return template_context


from ..forms import create_form_class_assinar, create_form_class_adicionar_assinantes


@register.filter
def class_name(object_instance):
    if object_instance:
        return object_instance.__class__.__name__
    return ''


@register.inclusion_tag('luzfcb_djdocuments/templatetags/boostrap3_modal.html', takes_context=True)
def render_modais_assinaturas_pendentes(context, context_name):
    forms = []
    ctx_name = 'djdocs_global'
    form_media = None

    # assinaturas_objs = context['to_modal_assinatura_pendente']
    ctx_name = 'djdocs_{}'.format(context_name)
    registered_contexts = []
    print(context.dicts[0].keys())
    for key in context.dicts[0].keys():
        key_str = key
        if key_str.startswith('djdocs_'):
            registered_contexts.append(key_str[7:])

    registered_contexts.append('maria')
    print('registered_contexts:', registered_contexts)
    try:
        assinaturas_objs = context[ctx_name]
    except KeyError:
        mgs = ' "{}" is not registered. the registered variables is: {}'.format(context_name,
                                                                                ', '.join(registered_contexts))
        raise KeyError(mgs)

    try:
        request = context['request']
    except KeyError:
        print('nao tem request no contexto')
    else:
        user = request.user
        for assinatura in assinaturas_objs:
            the_form = create_form_class_assinar(assinatura, user)
            form_instance = the_form(instance=assinatura, initial={'assinado_por': user})
            forms.append(form_instance)
        if forms:
            form_media = forms[0].media

    kwargs = {}
    djdocuments_backend = get_djdocuments_backend()
    document_object = context['object']
    grupos_ja_adicionados = document_object.grupos_assinates.all()
    grupo_para_adicionar_queryset = djdocuments_backend.get_grupos(
        excludes=grupos_ja_adicionados)
    kwargs.update({'grupo_para_adicionar_queryset': grupo_para_adicionar_queryset})

    adicionar_assinantes_form = create_form_class_adicionar_assinantes(document_object)
    adicionar_assinantes_form_instance = adicionar_assinantes_form(**kwargs)
    adicionar_assinantes_form_action = ''
    template_context = {
        'assinaturas_forms': forms,
        'assinatura_form_media': form_media + adicionar_assinantes_form_instance.media,
        'adicionar_assinantes_form_instance': adicionar_assinantes_form_instance,
        'adicionar_assinantes_form_action': adicionar_assinantes_form_action
    }
    return template_context


@register.simple_tag(takes_context=True)
def render_context(context, context_name, template='luzfcb_djdocuments/templatetags/boostrap3_modal.html'):
    forms = []
    ctx_name = 'djdocs_global'
    form_media = None

    # assinaturas_objs = context['to_modal_assinatura_pendente']
    ctx_name = 'djdocs_{}'.format(context_name)
    registered_contexts = []
    print(context.dicts[0].keys())
    for key in context.dicts[0].keys():
        key_str = key
        if key_str.startswith('djdocs_'):
            registered_contexts.append(key_str[7:])

    registered_contexts.append('maria')
    print('registered_contexts:', registered_contexts)
    try:
        assinaturas_objs = context[ctx_name]
    except KeyError:
        mgs = ' "{}" is not registered. the registered variables is: {}'.format(context_name,
                                                                                ', '.join(registered_contexts))
        raise KeyError(mgs)

    try:
        request = context['request']
    except KeyError:
        print('nao tem request no contexto')
    else:
        user = request.user
        for assinatura in assinaturas_objs:
            the_form = create_form_class_assinar(assinatura, user)
            form_instance = the_form(instance=assinatura, initial={'assinado_por': user})
            forms.append(form_instance)
        if forms:
            form_media = forms[0].media

    template_context = {
        'assinaturas_forms': forms,
        'assinatura_form_media': form_media
    }
    return render_to_string(template_name=template, context=template_context)


@register.filter
def add_defer(value):
    new_tags = []
    tags = value.render().split('\n')
    for tag in tags:
        new = tag
        if 'script' in new and not 'defer' in new:
            new = new.replace('<script', '<script defer')
        new_tags.append(new)

    return mark_safe('\n'.join(new_tags))
