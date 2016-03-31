# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0002_auto_20160329_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='tipo_documento_descricao',
            field=models.CharField(max_length=1000, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tipo_documento_descricao',
            field=models.CharField(max_length=1000, blank=True),
        ),
    ]
