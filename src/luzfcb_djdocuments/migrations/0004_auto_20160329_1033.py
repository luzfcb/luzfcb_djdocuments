# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0003_auto_20160329_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='tipo_documento_descricao',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='tipo_documento_descricao',
            field=models.TextField(blank=True),
        ),
    ]
