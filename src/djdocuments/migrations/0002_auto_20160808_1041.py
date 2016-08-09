# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assinatura',
            name='grupo_assinante',
            field=models.ForeignKey(related_name='djdocuments_assinatura_assinaturas', to='contrib.Defensoria'),
        ),
        migrations.AlterField(
            model_name='documento',
            name='grupo_dono',
            field=models.ForeignKey(related_name='djdocuments_documento_donos', to='contrib.Defensoria', null=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='grupos_assinates',
            field=models.ManyToManyField(to='contrib.Defensoria', through='djdocuments.Assinatura'),
        ),
        migrations.AlterField(
            model_name='historicaldocumento',
            name='grupo_dono',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='contrib.Defensoria', null=True),
        ),
    ]
