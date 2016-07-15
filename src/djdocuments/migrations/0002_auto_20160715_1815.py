# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='data_assinado',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='esta_assinado',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='data_assinado',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='esta_assinado',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
