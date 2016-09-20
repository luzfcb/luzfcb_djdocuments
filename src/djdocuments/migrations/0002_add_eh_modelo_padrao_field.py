# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='eh_modelo_padrao',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='eh_modelo_padrao',
            field=models.BooleanField(default=False),
        ),
    ]
