# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0003_auto_20160727_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assinatura',
            old_name='nome_defensoria',
            new_name='grupo_assinante_nome',
        ),
    ]
