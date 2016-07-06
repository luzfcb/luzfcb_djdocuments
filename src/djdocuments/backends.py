
from django.db.models import Q
from django.utils import timezone


class DocumentosBaseBackend(object):
    def pode_assinar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_editar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_visualizar(self, document, usuario, **kwargs):
        raise NotImplemented

    def pode_revogar_assinatura(self, document, usuario, **kwargs):
        raise NotImplemented


class DocumentosAuthGroupBackend(DocumentosBaseBackend):
    pass


class SolarDefensoriaBackend(DocumentosBaseBackend):
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
