# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0003_documentotemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='cabecalho',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='rodape',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='cabecalho',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='rodape',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='conteudo',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='titulo',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='conteudo',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='titulo',
            field=models.TextField(blank=True),
        ),
    ]
