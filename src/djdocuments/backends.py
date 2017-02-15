# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from collections import Iterable

from django.core.exceptions import ImproperlyConfigured

from .utils import get_djdocuments_backend, get_grupo_assinante_model_class


class DjDocumentsBackendMixin(object):

    def __init__(self, *args, **kwargs):
        super(DjDocumentsBackendMixin, self).__init__(*args, **kwargs)
        self.djdocuments_backend = get_djdocuments_backend()


class DjDocumentsBaseBackend(object):
    group_name_atrib = None
    group_label = None

    def pode_criar_documento_para_grupo(self, usuario, grupo):
        raise NotImplemented()

    def pode_remover_assinatura(self, document, assinatura, usuario_atual, **kwargs):
        raise NotImplemented()

    def get_usuarios_grupo(self, grupo, **kwargs):
        raise NotImplemented()

    def get_grupos(self, excludes=None):
        if excludes:
            if not isinstance(excludes, Iterable):
                excludes = [excludes]
            return get_grupo_assinante_model_class().objects.all().exclude(id__in=excludes)
        return get_grupo_assinante_model_class().objects.all()

    def get_grupo_model(self):
        return get_grupo_assinante_model_class()

    def get_grupo(self, **kwargs):
        use_filter = kwargs.pop('use_filter', False)
        if use_filter:
            return get_grupo_assinante_model_class().objects.filter(**kwargs)
        return get_grupo_assinante_model_class().objects.get(**kwargs)

    def get_grupo_name(self, grupo):
        return getattr(grupo, self.group_name_atrib)

    def get_group_label(self):
        if not self.group_label:
            raise ImproperlyConfigured(
                "%(cls)s nao possui a variavel group_label. Defina "
                "%(cls)s.group_label, ou sobreescreva o metodo"
                "%(cls)s.get_group_label()." % {
                    'cls': self.__class__.__name__
                }
            )
        return self.group_label

    def get_grupos_usuario(self, usuario):
        raise NotImplemented()

    def pode_assinar(self, document, usuario, **kwargs):
        raise NotImplemented()

    def pode_excluir_documento(self, document, usuario, **kwargs):
        raise NotImplemented()

    def pode_editar(self, document, usuario, **kwargs):
        raise NotImplemented()

    def pode_visualizar(self, document, usuario, **kwargs):
        raise NotImplemented()

    def pode_revogar_assinatura(self, document, usuario, **kwargs):
        raise NotImplemented()

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        return NotImplemented()


class AuthGroupDjDocumentsBackend(DjDocumentsBaseBackend):
    group_name_atrib = 'name'
    group_label = 'Grupo de usuario'

    def pode_remover_assinatura(self, document, assinatura, usuario_atual, **kwargs):
        if document == assinatura.documento:
            pks_grupos = tuple(self.get_grupos_usuario(usuario=usuario_atual).values_list('id', flat=True))
            return True if document.grupo_dono.pk in pks_grupos else False
        return False

    def get_usuarios_grupo(self, grupo, **kwargs):
        if not isinstance(grupo, self.get_grupo_model()):
            grupo = self.get_grupo_model().objects.get(pk=grupo)
        return grupo.user_set.filter(**kwargs)

    def get_grupo_name(self, grupo):
        return getattr(grupo, self.group_name_atrib)

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        grupo_assinante = kwargs.get('grupo_assinante')
        if grupo_assinante:
            grupos = [grupo_assinante.pk]
        else:
            grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.assinaturas.filter(grupo_assinante__in=grupos, esta_assinado=True).exists()

    def get_assinaturas_pendentes(self, document, usuario, **kwargs):
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.assinaturas.filter(id__in=grupos)

    def pode_visualizar(self, document, usuario, **kwargs):
        """
        :param document: Uma instancia de Documento
        :param usuario:
        :return: bool
        """
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.grupos_assinates.filter(id__in=grupos).exists()

    def pode_revogar_assinatura(self, document, usuario, **kwargs):
        return True

    def pode_editar(self, document, usuario, **kwargs):
        if document.esta_pronto_para_assinar:
            return False
        if document.criado_por == usuario:
            return True
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.assinaturas.filter(grupo_assinante__in=grupos).exists()

    def pode_assinar(self, document, usuario, **kwargs):
        grupo_assinante = kwargs.get('grupo_assinante')
        if grupo_assinante:
            return usuario.groups.filter(id=grupo_assinante.pk).exists()
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.grupos_assinates.filter(id__in=grupos).exists()

    def get_grupos_usuario(self, usuario):
        return usuario.groups.all()
