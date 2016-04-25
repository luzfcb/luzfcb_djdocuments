# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0004_auto_20160329_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='template_descricao',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='template_descricao',
            field=models.TextField(blank=True),
        ),
    ]
