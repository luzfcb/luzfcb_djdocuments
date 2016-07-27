# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0002_auto_20160715_1815'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assinatura',
            old_name='data_cadastro',
            new_name='cadastrado_em',
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='data_exclusao',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assinatura',
            name='excluido_por',
            field=models.ForeignKey(related_name='djdocuments_assinatura_excluido_por', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
