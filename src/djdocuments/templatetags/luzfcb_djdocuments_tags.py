# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import uuid

import bleach
from django import template
from django.db import models
from django.forms import Media
from django.forms.models import modelform_factory
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from django.utils import six
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


from ..forms import create_form_class_assinar, create_form_class_adicionar_assinantes, create_form_class_finalizar


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


DJDOCS_CONTEXT = 'djdocs_contexts'


def get_djdocs_context(context):
    if not context.dicts[0].get(DJDOCS_CONTEXT):
        context.dicts[0][DJDOCS_CONTEXT] = {}
    return context.dicts[0].get(DJDOCS_CONTEXT)


@register.simple_tag(takes_context=True)
def add_to_named_context(context, new_context_name_key, new_context_value, use_template=True,
                         template_name=None):
    base_template_dir = 'luzfcb_djdocuments/templatetags'
    template_name_suffix = 'a_element'
    return_value = ''
    new_context_name = six.text_type(new_context_name_key)
    djdocs_context = get_djdocs_context(context)

    if not djdocs_context.get(new_context_name):
        djdocs_context[new_context_name] = []

    new_context = djdocs_context.get(new_context_name)

    data = {
        'uuid': six.text_type(uuid.uuid4()),
        'object': new_context_value
    }
    new_context.append(data)

    if use_template or template_name:
        if not template_name:
            if isinstance(new_context_value, models.Model):
                object_meta = new_context_value._meta
                template_name = "%s/%s_%s_%s.html" % (
                    # object_meta.app_label,
                    base_template_dir,
                    new_context_name,
                    object_meta.model_name,
                    template_name_suffix
                )
            else:
                template_name = 'luzfcb_djdocuments/teste_add_to_named_context.html'
        return_value = render_to_string(template_name=template_name, context=data)
    return return_value


def gerar_forms_assinaturas_pendentes(context, context_name='assinaturas_pendentes'):
    forms = []
    form_media = None
    djdocs_context = get_djdocs_context(context)
    values_dict_to_render = djdocs_context.get(context_name, [])
    user = context['request'].user
    for valor in values_dict_to_render:
        assinatura = valor.get('object')
        _uuid = valor.get('uuid')
        if assinatura:
            the_form = create_form_class_assinar(assinatura, user)
            form_instance = the_form(instance=assinatura, initial={'assinado_por': user})
            forms.append((_uuid, form_instance))
    if forms:
        form_media = forms[0][1].media
    return forms, form_media


def gerar_form_adicionar_assinantes(context, context_name='adicionar_assinante'):
    form_kwargs = {}
    forms = []
    form_media = None
    djdocs_context = get_djdocs_context(context)
    values_dict_to_render = djdocs_context.get(context_name, [])

    djdocuments_backend = get_djdocuments_backend()
    for valor in values_dict_to_render:
        document_object = valor.get('object')
        _uuid = valor.get('uuid')
        if document_object:
            grupos_ja_adicionados = document_object.grupos_assinates.all()
            grupo_para_adicionar_queryset = djdocuments_backend.get_grupos(
                excludes=grupos_ja_adicionados)
            form_kwargs.update({'grupo_para_adicionar_queryset': grupo_para_adicionar_queryset})
            adicionar_assinantes_form = create_form_class_adicionar_assinantes(document_object)
            adicionar_assinantes_form_instance = adicionar_assinantes_form(**form_kwargs)
            forms.append((_uuid, adicionar_assinantes_form_instance))
    if forms:
        form_media = forms[0][1].media
    return forms, form_media


def gerar_forms_finalizar_documento(context, context_name='finalizar_documento'):
    form_kwargs = {}
    forms = []
    form_media = None
    djdocs_context = get_djdocs_context(context)
    values_dict_to_render = djdocs_context.get(context_name, [])
    user = context['request'].user
    djdocuments_backend = get_djdocuments_backend()
    for valor in values_dict_to_render:
        document_object = valor.get('object')
        _uuid = valor.get('uuid')
        if document_object:
            form_kwargs['current_logged_user'] = user
            group_id = document_object.grupo_dono.pk
            group_queryset = djdocuments_backend.get_grupo_model().objects.filter(pk=group_id)
            # kwargs['grupo_escolhido'] = None
            if group_id:
                form_kwargs['grupo_escolhido_queryset'] = group_queryset
                form_kwargs['grupo_escolhido'] = document_object.grupo_dono

            finalizar_documento_form = create_form_class_finalizar(document_object)
            finalizar_documento_form_instance = finalizar_documento_form(**form_kwargs)
            forms.append((_uuid, finalizar_documento_form_instance))
    if forms:
        form_media = forms[0][1].media
    return forms, form_media


@register.simple_tag(takes_context=True)
def render_named_context(context, context_name, template='luzfcb_djdocuments/templatetags/boostrap3_modal.html'):
    forms_media = Media()
    # djdocs_context = get_djdocs_context(context)
    # values_dict_to_render = djdocs_context.get(context_name)
    forms_assinaturas, form_media_assinaturas = gerar_forms_assinaturas_pendentes(context)
    forms_adicionar_assinantes, form_media_adicionar_assinantes = gerar_form_adicionar_assinantes(context)
    forms_finalizar_documento, form_media_finalizar_documento = gerar_form_adicionar_assinantes(context)
    for f in [form_media_assinaturas, form_media_finalizar_documento, form_media_adicionar_assinantes]:
        if f:
            forms_media = forms_media + f

    template_context = {
        'finalizar_forms': forms_finalizar_documento,
        'assinaturas_pendentes_forms': forms_assinaturas,
        'adicionar_assinantes_forms': forms_adicionar_assinantes,
        # 'assinatura_form_media': form_media
        'forms_media': forms_media
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
