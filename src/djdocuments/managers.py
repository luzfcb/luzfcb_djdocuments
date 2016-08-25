from django.db import models
from django.db.models import Case, IntegerField, Q, Sum, Value, When


class DocumentoQuerySet(models.QuerySet):

    def ativos(self):
        return self.filter(esta_ativo=True)

    def inativos(self):
        return self.filter(esta_ativo=False)

    def assinados(self):
        return self.filter(esta_assinado=True, esta_ativo=True)

    def prontos_para_finalizar(self, grupos_ids=None):
        q = Q()
        q &= Q(esta_assinado=False)
        if grupos_ids and isinstance(grupos_ids, (list, tuple)):
            q &= Q(grupo_dono__in=grupos_ids)
        qs = self.filter(q).annotate(
            assinaturas_pendentes=Sum(Case(When(assinaturas__esta_assinado=False, then=Value(1)), default=0,
                                           output_field=IntegerField()))).filter(assinaturas_pendentes=0)
        return qs


class DocumentoManager(models.Manager):
    queryset_class = DocumentoQuerySet

    def get_queryset(self):
        return self.queryset_class(model=self.model,
                                   using=self._db,
                                   hints=self._hints).ativos().filter(eh_modelo=False)

    def prontos_para_finalizar(self, grupos_ids=None):
        return self.get_queryset().prontos_para_finalizar(grupos_ids=grupos_ids)


class DocumentoAdminManager(models.Manager):
    queryset_class = DocumentoQuerySet

    def get_queryset(self):
        return self.queryset_class(model=self.model, using=self._db, hints=self._hints)


class AssinaturaQuerySet(models.QuerySet):
    pass


class AssinaturaManager(models.Manager):
    queryset_class = AssinaturaQuerySet

    def get_queryset(self):
        return self.queryset_class(model=self.model, using=self._db, hints=self._hints).select_related('documento')

    def ultimas_assinaturas_realizadas(self, grupos_ids=None):
        q = Q()
        q &= ~Q(assinado_por=None)
        q &= Q(ativo=True)
        if grupos_ids and isinstance(grupos_ids, (list, tuple)):
            q &= Q(grupo_assinante_id__in=grupos_ids)

        return self.get_queryset().select_related('grupo_assinante').filter(q).order_by('cadastrado_em')

    def ultimas_assinaturas_pendentes(self, grupos_ids=None):
        q = Q()
        q &= Q(assinado_por=None)
        q &= Q(ativo=True)
        if grupos_ids and isinstance(grupos_ids, (list, tuple)):
            q &= Q(grupo_assinante_id__in=grupos_ids)
        return self.get_queryset().select_related('grupo_assinante').filter(q).order_by('cadastrado_em')
