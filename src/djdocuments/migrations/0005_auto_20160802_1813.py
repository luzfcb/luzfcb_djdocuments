# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('djdocuments', '0004_auto_20160802_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='grupo_dono',
            field=models.ForeignKey(related_name='djdocuments_documento_donos', to='auth.Group', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='grupo_dono',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='auth.Group', null=True),
        ),
    ]
