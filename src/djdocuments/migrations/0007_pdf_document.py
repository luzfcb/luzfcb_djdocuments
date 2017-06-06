# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0006_add_documento_pk_uuid_e_outros_em_assinatura'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to='djdocuments')),
                ('documento_pk_uuid', models.UUIDField(null=True, editable=False, db_index=True)),
                ('documento_identificador_versao', models.CharField(max_length=25, editable=False, blank=True)),
                ('documento', models.OneToOneField(related_name='pdf', to='djdocuments.Documento')),
            ],
        ),
    ]
