# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='assunto',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='assunto',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
