from django.db import models
from django.db.models import Case, IntegerField, Q, Sum, Value, When
from django.db.models.query import ValuesListQuerySet


class DocumentoQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(esta_ativo=True)

    def inativos(self):
        return self.filter(esta_ativo=False)

    def assinados(self):
        return self.filter(esta_assinado=True, esta_ativo=True)

    def prontos_para_finalizar(self):

        q = Q()
        q &= Q(esta_assinado=False)
        q &= Q(eh_modelo=False)
        # if grupos_ids and not isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
        #     raise ValueError(
        #         "on %s: Expect list, tuple or ValuesListQuerySet"
        #         % self.__class__.__name__
        #     )
        # if grupos_ids and isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
        #     q &= Q(grupo_dono__in=grupos_ids)
        qs = self.filter(q).annotate(
            assinaturas_pendentes=Sum(Case(When(assinaturas__esta_assinado=False, then=Value(1)), default=0,
                                           output_field=IntegerField()))).filter(assinaturas_pendentes=0)
        return qs

    def from_groups(self, grupos_ids):
        q = Q()
        qs = self.none()
        if not isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            raise ValueError(
                "on %s: Expect list, tuple or ValuesListQuerySet"
                % self.__class__.__name__
            )
        if grupos_ids:
            q &= Q(grupo_dono__in=grupos_ids)
            qs = self.filter(q)
        return qs

    def modelos(self, grupos_ids=None):
        q = Q()
        q &= Q(eh_modelo=True)
        if grupos_ids and not isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            raise ValueError(
                "on %s: Expect list, tuple or ValuesListQuerySet"
                % self.__class__.__name__
            )
        if grupos_ids and isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            q &= Q(grupo_dono__in=grupos_ids)
        qs = self.filter(q)
        return qs

    def documentos_dos_grupos(self, grupos_ids=None):
        q = Q()
        q &= Q(eh_modelo=False)
        if grupos_ids and not isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            raise ValueError(
                "on %s: Expect list, tuple or ValuesListQuerySet"
                % self.__class__.__name__
            )
        if grupos_ids and isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            q &= Q(grupo_dono__in=grupos_ids)
        qs = self.filter(q)
        return qs


class DocumentoManager(models.Manager):
    _queryset_class = DocumentoQuerySet

    def get_queryset(self):
        return self._queryset_class(model=self.model,
                                    using=self._db,
                                    hints=self._hints).ativos().filter(eh_modelo=False)

    def prontos_para_finalizar(self):
        return self.get_queryset().prontos_para_finalizar()

    def from_groups(self, grupos_ids):
        return self.get_queryset().from_groups(grupos_ids=grupos_ids)

    def modelos(self, grupos_ids=None):
        return self._queryset_class(model=self.model,
                                    using=self._db,
                                    hints=self._hints).ativos().modelos(grupos_ids=grupos_ids)

    def documentos_dos_grupos(self, grupos_ids=None):
        return self._queryset_class(model=self.model,
                                    using=self._db,
                                    hints=self._hints).ativos().documentos_dos_grupos(grupos_ids=grupos_ids)


class DocumentoAdminManager(models.Manager):
    _queryset_class = DocumentoQuerySet

    def get_queryset(self):
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)

    def prontos_para_finalizar(self):
        return self.get_queryset().prontos_para_finalizar()

    def from_groups(self, grupos_ids):
        return self.get_queryset().from_groups(grupos_ids=grupos_ids)

    def modelos(self, grupos_ids=None):
        return self._queryset_class(model=self.model,
                                    using=self._db,
                                    hints=self._hints).ativos().modelos(grupos_ids=grupos_ids)

    def documentos_dos_grupos(self, grupos_ids=None):
        return self._queryset_class(model=self.model,
                                    using=self._db,
                                    hints=self._hints).ativos().documentos_dos_grupos(grupos_ids=grupos_ids)


class AssinaturaQuerySet(models.QuerySet):
    def assinaturas_realizadas(self):
        q = Q()
        q &= Q(documento__eh_modelo=False)
        q &= ~Q(assinado_por=None)
        q &= Q(ativo=True)
        qs = self.select_related('grupo_assinante').filter(q)
        return qs

    def assinaturas_pendentes(self):
        q = Q()
        q &= Q(documento__eh_modelo=False)
        q &= Q(assinado_por=None)
        q &= Q(ativo=True)
        qs = self.select_related('grupo_assinante').filter(q)
        return qs

    def from_groups(self, grupos_ids):
        q = Q()
        qs = self.none()
        if not isinstance(grupos_ids, (list, tuple, ValuesListQuerySet)):
            raise ValueError(
                "on %s: Expect list, tuple or ValuesListQuerySet"
                % self.__class__.__name__
            )
        if grupos_ids:
            q &= Q(grupo_assinante_id__in=grupos_ids)
            qs = self.filter(q)
        return qs


class AssinaturaManager(models.Manager):
    _queryset_class = AssinaturaQuerySet

    def get_queryset(self):
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints).select_related('documento')

    def assinaturas_realizadas(self):
        return self.get_queryset().assinaturas_realizadas()

    def assinaturas_pendentes(self):
        return self.get_queryset().assinaturas_pendentes()

    def from_groups(self, grupos_ids):
        return self.get_queryset().from_groups(grupos_ids=grupos_ids)
