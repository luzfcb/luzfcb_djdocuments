# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django_tables2

from . import models


class DocumentoTable(django_tables2.Table):
    documento = django_tables2.LinkColumn(verbose_name='Documento',
                                          text=lambda record: record.identificador_versao,
                                          attrs={
                                              'a': {'class': 'btn-link'}
                                          }
                                          )

    acoes = django_tables2.TemplateColumn(verbose_name='Ações',
                                          template_name='luzfcb_djdocuments/tables2/botoes_acao_listar_documento.html',
                                          attrs={
                                              'td': {'class': 'text-center'}
                                          }
                                          )

    class Meta:

        template = 'luzfcb_djdocuments/tables2/bootstrap.html'
        model = models.Documento
        fields = ('documento', 'tipo_documento', 'grupo_dono', 'assunto', 'criado_em', 'modificado_em', 'acoes')
