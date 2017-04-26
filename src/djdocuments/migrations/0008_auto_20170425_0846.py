# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0007_pdf_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='excluido_por_nome',
            field=models.CharField(default='', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='excluido_por_nome',
            field=models.CharField(default='', max_length=255, blank=True),
        ),
    ]
