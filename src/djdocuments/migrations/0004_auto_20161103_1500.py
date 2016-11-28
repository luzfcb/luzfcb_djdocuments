# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0003_unaccent_pg_extension'),
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
