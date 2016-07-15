from django.db import models  # noqa


class Processo(models.Model):
    nome = models.CharField(max_length=255)
    documentos = models.ManyToManyField('djdocuments.Documento',
                                        related_name='%(app_label)s_%(class)s_Processo',
                                        blank=True)
