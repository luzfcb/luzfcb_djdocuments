# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from dal import autocomplete
from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .. import models
from ..templatetags.luzfcb_djdocuments_tags import remover_tags_html
from ..views.documentos import USER_MODEL
from ..utils import get_grupo_assinante_backend
from ..views.auth_mixins import LoginRequiredMixin
from .mixins import SingleDocumentObjectMixin


class GrupoAindaNaoAssinantesDoDocumentoAutoComplete(LoginRequiredMixin,
                                          SingleDocumentObjectMixin,
                                          autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()
        backend = get_grupo_assinante_backend()

        grupos_assinantes_ja_incluidos = self.document_object.grupos_assinates.values_list('id',
                                                                                           flat=True)

        qs = backend.get_grupos(excludes=grupos_assinantes_ja_incluidos)

        if self.q:
            paran_dict = {'{}__icontains'.format(backend.group_name_atrib): self.q}
            qs = qs.filter(Q(paran_dict))

        return qs

    def get_result_label(self, result):
        return get_grupo_assinante_backend().get_grupo_name(result)


class GruposAssinantesDoDocumentoAutoComplete(LoginRequiredMixin,
                                              SingleDocumentObjectMixin,
                                              autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()
        backend = get_grupo_assinante_backend()

        assinaturas = self.document_object.assinaturas.filter(assinado_por=None).values_list('grupo_assinante_id',
                                                                                             flat=True)
        qs = self.document_object.grupos_assinates.filter(id__in=assinaturas)

        if self.q:
            paran_dict = {'{}__icontains'.format(backend.group_name_atrib): self.q}
            qs = qs.filter(Q(paran_dict))

        return qs

    def get_result_label(self, result):
        return get_grupo_assinante_backend().get_grupo_name(result)


class GruposDoUsuarioAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()
        backend = get_grupo_assinante_backend()
        qs = backend.get_grupos_usuario(self.request.user)

        if self.q:
            paran_dict = {'{}__icontains'.format(backend.group_name_atrib): self.q}
            qs = qs.filter(Q(paran_dict))

        return qs

    def get_result_label(self, result):
        return get_grupo_assinante_backend().get_grupo_name(result)


class UsersByGroupAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """
    UsersByGroupAutocomplete view to Django User Based filter by group
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()
        backend = get_grupo_assinante_backend()

        grupo = self.forwarded.get('grupo', None)
        if grupo:
            qs = backend.get_usuarios_grupo(grupo).order_by('first_name', 'last_name')
        else:
            qs = USER_MODEL.objects.none()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

        return qs

    def get_result_label(self, result):
        name, user_name = result.get_full_name().title(), getattr(result, result.USERNAME_FIELD)
        return '{} ({})'.format(name, user_name)


class UserAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return USER_MODEL.objects.none()
        backend = get_grupo_assinante_backend()
        assinado_por = self.forwarded.get('assinado_por', None)
        grupo = self.forwarded.get('grupo', 'teste')
        print("grupo:", grupo)
        if grupo:
            if grupo == 'null':
                qs = USER_MODEL.objects.none()
            else:
                qs = backend.get_usuarios_grupo(grupo).order_by('first_name', 'last_name')
        else:
            qs = USER_MODEL.objects.all().order_by('first_name', 'last_name')

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

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
