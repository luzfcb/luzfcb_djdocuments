# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documento',
            name='modelo_documento',
        ),
        migrations.RemoveField(
            model_name='historicaldocumento',
            name='modelo_documento',
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo_documento',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tipo_documento',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
