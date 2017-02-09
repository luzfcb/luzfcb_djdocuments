# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0004_adicionado_margens_pdf_no_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
