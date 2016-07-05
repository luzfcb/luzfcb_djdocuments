from django.contrib.auth.models import Group
from djdocuments.backends import DocumentosBaseBackend


class AuthGroupDocumentosBackend(DocumentosBaseBackend):
    def pode_visualizar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante):
        return True

    def pode_revogar_assinatura(self, document, usuario_assinante, grupo_assinante):
        return True

    def pode_editar_documento_para_o_grupo(self, document, usuario_assinante):
        return True

    def pode_assinar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante, now_datetime):
        return True
