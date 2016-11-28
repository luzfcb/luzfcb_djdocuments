# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0002_add_eh_modelo_padrao_field'),
    ]

    operations = [
        UnaccentExtension()
    ]
