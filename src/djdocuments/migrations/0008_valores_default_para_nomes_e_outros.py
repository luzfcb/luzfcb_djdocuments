# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0007_pdf_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assinatura',
            name='data_exclusao',
            field=models.DateTimeField(null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='excluido_por',
            field=models.ForeignKey(related_name='djdocuments_assinatura_excluido_por', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='nome_cadastrado_por',
            field=models.CharField(max_length=255, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='nome_excluido_por',
            field=models.CharField(default='', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='excluido_por_nome',
            field=models.CharField(default='', max_length=255, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='excluido_por_nome',
            field=models.CharField(default='', max_length=255, editable=False, blank=True),
        ),
    ]
