# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-07 14:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luzfcb_djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='eh_template',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='eh_template',
            field=models.BooleanField(default=False),
        ),
    ]
