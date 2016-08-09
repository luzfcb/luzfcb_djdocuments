# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0002_auto_20160808_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='grupo_dono',
            field=models.ForeignKey(related_name='djdocuments_documento_donos', blank=True, to='contrib.Defensoria', null=True),
        ),
    ]
