# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def marcar_modelos_sem_grupo_dono_como_publicos(apps, schema_editor):
    Documento = apps.get_model('djdocuments', 'Documento')
    documentos = Documento.objects.filter(
        eh_modelo=True,
        grupo_dono=None,
    ).update(
        modelo_publico=True
    )


def reverter_marcar_modelos_sem_grupo_dono_como_publicos(apps, schema_editor):
    Documento = apps.get_model('djdocuments', 'Documento')
    documentos = Documento.objects.filter(
        eh_modelo=True,
        grupo_dono=None,
    ).update(
        modelo_publico=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0015_popular_dados_finalizado_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='modelo_publico',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='modelo_publico',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            code=marcar_modelos_sem_grupo_dono_como_publicos,
            reverse_code=reverter_marcar_modelos_sem_grupo_dono_como_publicos,
            atomic=True
        )
    ]
