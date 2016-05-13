# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-12 19:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('luzfcb_djdocuments', '0004_auto_20160512_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='assinatura',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='modificado_por',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='luzfcb_djdocuments_assinatura_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]