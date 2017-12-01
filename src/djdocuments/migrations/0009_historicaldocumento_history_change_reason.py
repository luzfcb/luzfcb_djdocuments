# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0008_valores_default_para_nomes_e_outros'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaldocumento',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
