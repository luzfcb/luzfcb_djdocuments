# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0011_todos_modelo_pronto_para_utilizacao_como_true'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='rodape_assinatura',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='rodape_assinatura',
            field=models.TextField(default='', blank=True),
        ),
    ]
