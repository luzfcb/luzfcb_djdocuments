# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0009_historicaldocumento_history_change_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='modelo_pronto_para_utilizacao',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='modelo_pronto_para_utilizacao',
            field=models.BooleanField(default=False),
        ),
    ]
