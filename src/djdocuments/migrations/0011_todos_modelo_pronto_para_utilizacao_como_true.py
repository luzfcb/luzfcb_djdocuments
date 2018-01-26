# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import migrations, models


def mudar_todos_modelos_para_pronto_para_utilizacao(apps, schema_editor):
    Documento = apps.get_model('djdocuments', 'Documento')
    modelos = Documento.objects.filter(eh_modelo=True, esta_ativo=True)
    modelos.update(modelo_pronto_para_utilizacao=True)


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0010_add_modelo_pronto_para_utilizacao'),
    ]

    operations = [
        migrations.RunPython(code=mudar_todos_modelos_para_pronto_para_utilizacao, atomic=True)
    ]
