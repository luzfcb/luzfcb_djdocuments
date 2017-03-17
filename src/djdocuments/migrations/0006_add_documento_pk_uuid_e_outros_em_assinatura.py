# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from djdocuments.utils import identificador


def populate_new_assinatura_fields(apps, schema_editor):
    """
    Updates the db field in all Version models to point to the correct write
    db for the model.
    """
    db_alias = schema_editor.connection.alias
    Assinatura = apps.get_model("djdocuments", "Assinatura")
    assinaturas = Assinatura.objects.using(db_alias).select_related('documento')

    for assinatura in assinaturas:
        if assinatura.documento:
            if not assinatura.documento_pk_uuid:
                assinatura.documento_pk_uuid = assinatura.documento.pk_uuid
            if not assinatura.documento_assunto:
                assinatura.documento_assunto = assinatura.documento.assunto
            if not assinatura.documento_identificador_versao:
                assinatura.documento_identificador_versao = identificador.document(assinatura.documento.pk,
                                                                                   assinatura.documento.versao_numero)
            assinatura.save()


def populate_new_assinatura_fields_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0005_field_de_exclusao'),
    ]

    operations = [
        migrations.AddField(
            model_name='assinatura',
            name='documento_pk_uuid',
            field=models.UUIDField(null=True, editable=False, db_index=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='documento_assunto',
            field=models.CharField(max_length=255, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='documento_identificador_versao',
            field=models.CharField(max_length=25, editable=False, blank=True),
        ),
        migrations.RunPython(populate_new_assinatura_fields, populate_new_assinatura_fields_reverse),
    ]
