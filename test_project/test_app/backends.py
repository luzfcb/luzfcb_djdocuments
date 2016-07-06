from django.contrib.auth.models import Group, User
from django.utils import timezone
from djdocuments.backends import DocumentosBaseBackend
from django.db.models import Q


class AuthGroupDocumentosBackend(DocumentosBaseBackend):
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
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.assinaturas.filter(grupo_assinante__in=grupos).exists()

    def pode_assinar(self, document, usuario, **kwargs):
        grupo_assinante = kwargs.get('grupo_assinante')
        if grupo_assinante:
            return usuario.groups.filter(id=grupo_assinante.pk).exists()
        grupos = tuple(usuario.groups.all().values_list('id', flat=True))
        return document.grupos_assinates.filter(id__in=grupos).exists()
