# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    from django.contrib.auth import get_user_model
    User = get_user_model()
    TipoDocumento = apps.get_model('djdocuments', 'TipoDocumento')
    Documento = apps.get_model('djdocuments', 'Documento')
    # user1 =
    # tipo_documento1 = TipoDocumento.objects.create(titulo='tipo1', descricao='desc tipo1')
    # template_doc1 = Documento.objects.create(tipo_documento=tipo_documento1,
    #                                              eh_template=True,
    #                                              cabecalho='template1',
    #                                              rodape='template1',
    #                                              conteudo='template1',
    #                                              titulo='template1',
    #                                              criado_por=user1,
    #                                              modificado_por=user1,
    #                                              )
    # Your migration code goes here


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
