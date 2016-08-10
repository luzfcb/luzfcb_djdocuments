# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0003_auto_20160808_1111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assinatura',
            name='esta_ativo',
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='ativo',
            field=models.NullBooleanField(default=True, editable=False),
        ),
    ]
