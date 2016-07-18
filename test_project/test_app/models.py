from django.db import models  # noqa
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Processo(models.Model):
    nome = models.CharField(max_length=255)
    documentos = models.ManyToManyField('djdocuments.Documento',
                                        related_name='processo',
                                        blank=True)

    def __str__(self):
        return "pk:{}".format(self.pk)
