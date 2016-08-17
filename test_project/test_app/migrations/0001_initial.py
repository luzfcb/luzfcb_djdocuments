# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('documentos', models.ManyToManyField(related_name='processo', to='djdocuments.Documento', blank=True)),
            ],
        ),
    ]
