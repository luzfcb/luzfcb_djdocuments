# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djdocuments', '0013_fix_pronto_para_assinar'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='finalizado_por',
            field=models.ForeignKey(related_name='djdocuments_documento_finalizado_por',
                                    on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False,
                                    to=settings.AUTH_USER_MODEL,
                                    help_text='Usuario que finalizou o documento para o sistema gere o c\xf3digo de valida\xe7\xe3o',
                                    null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='finalizado_por_nome',
            field=models.CharField(default='', max_length=255, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='finalizado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                    db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='finalizado_por_nome',
            field=models.CharField(default='', max_length=255, editable=False, blank=True),
        ),

    ]
