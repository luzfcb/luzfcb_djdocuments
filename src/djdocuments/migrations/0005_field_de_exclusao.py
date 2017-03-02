# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djdocuments', '0004_adicionado_margens_pdf_no_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='excluido_em',
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='documento',
            name='excluido_por',
            field=models.ForeignKey(related_name='djdocuments_documento_excluido_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='excluido_por_nome',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='excluido_em',
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='excluido_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='excluido_por_nome',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
