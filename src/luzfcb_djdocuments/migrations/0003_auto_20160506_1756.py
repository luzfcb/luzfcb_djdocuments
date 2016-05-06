# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('luzfcb_djdocuments', '0002_auto_20160505_0938'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assinatura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assinatura_hash', models.TextField(unique=True, null=True, editable=False, blank=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinado_por', models.ForeignKey(related_name='luzfcb_djdocuments_assinatura_assinado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('documento', models.ForeignKey(related_name='luzfcb_djdocuments_assinatura_documento', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='luzfcb_djdocuments.Documento', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='documento',
            name='assinantes',
            field=models.ManyToManyField(related_name='luzfcb_djdocuments_documento_assinantes', editable=False, to=settings.AUTH_USER_MODEL, through='luzfcb_djdocuments.Assinatura', blank=True),
        ),
    ]
