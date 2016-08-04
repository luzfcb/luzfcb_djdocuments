from django.db import models


class DocumentoQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(esta_ativo=True)

    def inativos(self):
        return self.filter(esta_ativo=False)

    def assinados(self):
        return self.filter(esta_assinado=True, esta_ativo=True)


class DocumentoManager(models.Manager):
    queryset_class = DocumentoQuerySet

    def get_queryset(self):
        return self.queryset_class(model=self.model,
                                   using=self._db,
                                   hints=self._hints).ativos().filter(eh_template=False)


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
