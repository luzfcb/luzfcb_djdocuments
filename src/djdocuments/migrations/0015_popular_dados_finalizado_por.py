# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrar_finalizado_por(apps, schema_editor):
    Documento = apps.get_model('djdocuments', 'Documento')
    documentos = Documento.objects.only(
        'eh_modelo',
        'esta_assinado',
    ).prefetch_related(
        'assinaturas',
    ).filter(
        eh_modelo=False,
        esta_assinado=True,
    )
    numero_docs = documentos.count()
    pks_docs_afetados = []
    for doc in documentos:
        ultima_assinatura = doc.assinaturas.order_by().order_by(
            '-assinado_em'
        ).filter(
            esta_assinado=True,
            ativo=True
        ).first()
        if ultima_assinatura:
            pks_docs_afetados.append(doc.pk)
            doc.finalizado_por_id = ultima_assinatura.assinado_por_id
            doc.finalizado_por_nome = ultima_assinatura.assinado_nome
            doc._desabilitar_temporiariamente_versao_numero = True
            doc.save()
    print('numero_de_documentos_afetados: {}'.format(numero_docs))
    print('pks doc afetados:')
    print(sorted(pks_docs_afetados))


def reverter_finalizado_por(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('djdocuments', '0014_add_campos_finalizado_por'),
    ]

    operations = [
        migrations.RunPython(
            code=migrar_finalizado_por,
            reverse_code=reverter_finalizado_por,
            atomic=True
        )
    ]
