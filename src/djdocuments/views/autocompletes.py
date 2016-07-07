# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from dal import autocomplete
from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .. import models
from ..templatetags.luzfcb_djdocuments_tags import remover_tags_html
from ..views.documentos import USER_MODEL


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()

        assinado_por = self.forwarded.get('assinado_por', None)

        qs = USER_MODEL.objects.all().order_by('first_name', 'last_name')

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

        if assinado_por:
            qs = qs.exclude(id=assinado_por)
            # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
            # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        name, user_name = result.get_full_name().title(), getattr(result, result.USERNAME_FIELD)
        return '{} ({})'.format(name, user_name)


# class DocumentoTemplateAutocomplete(autocomplete.Select2QuerySetView):
#     """
#     Autocomplete view to Django User Based
#     """
#
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return models.DocumentoTemplate.objects.none()
#
#         qs = models.DocumentoTemplate.objects.all()
#
#         if self.q:
#             qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
#
#             # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
#             # qs = qs.filter(full_name__icontains=self.q)
#         return qs
#
#     def get_result_label(self, result):
#         return result.get_full_name().title()


class DocumentoCriarAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoCriarAutocomplete, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return models.Documento.admin_objects.none()

        tipo_documento = self.forwarded.get('tipo_documento', None)

        qs = models.Documento.admin_objects.filter(eh_template=True)

        if tipo_documento:
            qs = qs.filter(tipo_documento_id=tipo_documento)
            if self.q:
                qs = qs.filter(template_descricao__icontains=self.q)

        else:
            qs = models.Documento.admin_objects.none()

        # if self.q:
        #     qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        #
        #     # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
        #     # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        a = remover_tags_html(result.template_descricao)
        return a
