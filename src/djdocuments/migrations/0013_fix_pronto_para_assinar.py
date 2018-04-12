# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def corrigir_campo_esta_pronto_para_assinar_docs_assinados_e_finalizados(apps, schema_editor):
    Documento = apps.get_model('djdocuments', 'Documento')
    documentos = Documento.objects.filter(
        eh_modelo=False,
        esta_ativo=True,
        esta_pronto_para_assinar=False,
        assinaturas__ativo=True,
        assinaturas__esta_assinado=True
    ).distinct()
    pks_afetados = list(documentos.values_list('pk', flat=True))
    pks_afetados = sorted(pks_afetados)
    documentos.update(esta_pronto_para_assinar=True)
    print('\n        Primary keys das intancias de djdocuments.models.Documento afetados:')
    print('        {}\n'.format(pks_afetados))


def fake_revert(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0012_add_rodape_qr_validacao_e_conteudo_assinaturas'),
    ]

    operations = [
        migrations.RunPython(
            code=corrigir_campo_esta_pronto_para_assinar_docs_assinados_e_finalizados,
            reverse_code=fake_revert,
            atomic=True
        )
    ]
