# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.db.models import Q
from django.utils import timezone


class DocumentosBaseBackend(object):
    group_name_atrib = None

    def get_grupo_name(self, grupo):
        return getattr(grupo, self.group_name_atrib)

    def get_grupos(self, usuario):
        raise NotImplemented

    def pode_assinar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_editar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_visualizar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_revogar_assinatura(self, document, usuario, **kwargs):
        raise NotImplemented

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        return NotImplemented


class AuthGroupDocumentosBackend(DocumentosBaseBackend):
    group_name_atrib = 'name'

    def get_grupo_name(self, grupo):
        return getattr(grupo, self.group_name_atrib)

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.assinaturas.filter(grupo_assinante__in=grupos, esta_assinado=True).exists()

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

    def get_grupos(self, usuario):
        return usuario.groups.all()


class SolarDefensoriaBackend(DocumentosBaseBackend):
    group_name_atrib = 'nome'

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        return NotImplemented

    def pode_visualizar(self, document, usuario, **kwargs):
        agora = timezone.now()
        usuario_atual_pode_visualizar = document.assinaturas.filter(
            Q(defensoria__all_atuacoes__ativo=True) &
            Q(defensoria__all_atuacoes__data_inicial__lte=agora) &
            (
                Q(defensoria__all_atuacoes__data_final__gte=agora) |
                Q(defensoria__all_atuacoes__data_final=None)
            ) &
            (
                Q(defensoria__all_atuacoes__defensor__servidor__usuario=usuario) |
                Q(defensoria__all_atuacoes__defensor__assessores__servidor__usuario=usuario)
            )
        ).exists()

        return usuario_atual_pode_visualizar

    def pode_editar(self, document, usuario, **kwargs):
        if document.esta_pronto_para_assinar:
            return False
        if document.criado_por == usuario:
            return True
        agora = timezone.now()
        usuario_atual_pode_editar = document.grupos_assinates.filter(
            Q(all_atuacoes__ativo=True) &
            Q(all_atuacoes__data_inicial__lte=agora) &
            (
                Q(all_atuacoes__data_final__gte=agora) |
                Q(all_atuacoes__data_final=None)
            ) &
            (
                Q(all_atuacoes__defensor__servidor__usuario=usuario) |
                Q(all_atuacoes__defensor__assessores__servidor__usuario=usuario)
            )
        ).exists()

        return usuario_atual_pode_editar

    def pode_assinar(self, document, usuario, **kwargs):
        grupo_assinante = kwargs.get('grupo_assinante')
        agora = timezone.now()
        defensorias = usuario.servidor.defensor.all_atuacoes.filter(
            Q(ativo=True) &
            Q(defensoria=grupo_assinante) &
            Q(data_inicial__lte=agora) &
            (
                Q(data_final__gte=agora) |
                Q(data_final=None)
            )
        ).exists()

        return bool(defensorias)

    def get_grupos(self, usuario):
        agora = timezone.now()
        defensorias = usuario.servidor.defensor.all_atuacoes.filter(
            Q(ativo=True) &
            Q(data_inicial__lte=agora) &
            (
                Q(data_final__gte=agora) |
                Q(data_final=None)
            )
        )
        return defensorias
