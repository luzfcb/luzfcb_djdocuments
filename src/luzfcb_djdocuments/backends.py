from django.db.models import Q
from django.utils import timezone


class DocumentosBaseBackend(object):

    def pode_assinar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante, now_datetime):
        raise NotImplemented

    def pode_editar_documento_para_o_grupo(self, document, usuario_assinante):
        raise NotImplemented

    def pode_visualizar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante):
        raise NotImplemented

    def pode_revogar_assinatura(self, document, usuario_assinante, grupo_assinante):
        raise NotImplemented


class DocumentosAuthGroupBackend(DocumentosBaseBackend):
    pass


class SolarDefensoriaBackend(DocumentosBaseBackend):

    def pode_visualizar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante):
        agora = timezone.now()
        usuario_atual_pode_visualizar = document.assinaturas.filter(
            Q(defensoria__all_atuacoes__ativo=True) &
            Q(defensoria__all_atuacoes__data_inicial__lte=agora) &
            (
                Q(defensoria__all_atuacoes__data_final__gte=agora) |
                Q(defensoria__all_atuacoes__data_final=None)
            ) &
            (
                Q(defensoria__all_atuacoes__defensor__servidor__usuario=usuario_assinante) |
                Q(defensoria__all_atuacoes__defensor__assessores__servidor__usuario=usuario_assinante)
            )
        ).exists()

        return usuario_atual_pode_visualizar

    def pode_editar_documento_para_o_grupo(self, document, usuario_assinante):
        if document.esta_pronto_para_assinar:
            return False
        agora = timezone.now()
        usuario_atual_pode_editar = document.grupos_assinates.filter(
            Q(all_atuacoes__ativo=True) &
            Q(all_atuacoes__data_inicial__lte=agora) &
            (
                Q(all_atuacoes__data_final__gte=agora) |
                Q(all_atuacoes__data_final=None)
            ) &
            (
                Q(all_atuacoes__defensor__servidor__usuario=usuario_assinante) |
                Q(all_atuacoes__defensor__assessores__servidor__usuario=usuario_assinante)
            )
        ).exists()

        return usuario_atual_pode_editar

    def pode_assinar_documento_para_o_grupo(self, document, usuario_assinante, grupo_assinante, now_datetime):
        defensorias = usuario_assinante.servidor.defensor.all_atuacoes.filter(
            Q(ativo=True) &
            Q(defensoria=grupo_assinante) &
            Q(data_inicial__lte=now_datetime) &
            (
                Q(data_final__gte=now_datetime) |
                Q(data_final=None)
            )
        ).exists()

        return bool(defensorias)
