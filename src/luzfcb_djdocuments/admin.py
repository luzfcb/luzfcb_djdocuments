# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import format_html

from simple_history.admin import SimpleHistoryAdmin

from . import models


# @admin.register(models.Documento)
class DocumentContentAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'criado_em', 'criado_por', 'modificado_em', 'modificado_por', 'revertido_em', 'revertido_por',
        'revertido_da_versao', 'esta_ativo', 'esta_bloqueado', 'versao_numero', 'visualizar_versao'
    )
    readonly_fields = ('criado_em', 'criado_por', 'modificado_em', 'modificado_por', 'revertido_em', 'revertido_por',
                       'revertido_da_versao',
                       )

    def visualizar_versao(self, obj):
        url_triplet = self.admin_site.name, self.model._meta.app_label, self.model._meta.model_name
        history_url = reverse('%s:%s_%s_history' % url_triplet,
                              args=(obj.pk,))
        html = format_html('<a href="{}">{}</a>'.format(history_url, 'Visualizar'))
        return html

    visualizar_versao.allow_tags = True
    visualizar_versao.short_description = "Visualizar Versões"


@admin.register(models.Documento)
class DocTeste(SimpleHistoryAdmin):
    list_display = (
        # 'criado_em', 'criado_por', 'versao_numero', 'assinatura_hash', 'visualizar_versao'
        'identificador_versao', 'esta_assinado', 'assinatura_hash', 'criado_em', 'titulo', 'criado_por',
        'modificado_em',
        'modificado_por', 'revertido_em', 'revertido_por',
        'revertido_da_versao', 'esta_ativo', 'esta_bloqueado', 'versao_numero', 'visualizar_versao',
        'assinado_em', 'assinado_por', 'assinatura_removida_em', 'assinatura_removida_por'
    )

    readonly_fields = (
        'identificador_versao',
        'assinatura_hash', 'assinado_em', 'assinado_por', 'criado_em', 'criado_por', 'modificado_em', 'modificado_por',
        'revertido_em',
        'revertido_por', 'revertido_da_versao',

    )
    # readonly_fields = ('criado_em', 'criado_por', 'modificado_em', 'modificado_por', 'revertido_em', 'revertido_por',
    #                    'revertido_da_versao',
    #                    )
    actions = ['remover_assinatura', ]

    def visualizar_versao(self, obj):
        url_triplet = self.admin_site.name, self.model._meta.app_label, self.model._meta.model_name
        history_url = reverse('%s:%s_%s_history' % url_triplet,
                              args=(obj.pk,))
        html = format_html('<a href="{}">{}</a>'.format(history_url, 'Visualizar'))
        return html

    visualizar_versao.allow_tags = True
    visualizar_versao.short_description = "Visualizar Versões"

    def remover_assinatura(self, request, queryset):
        queryset.update(assinatura_hash='', esta_assinado=False, assinado_em=None, assinado_por=None,
                        assinatura_removida_em=timezone.now(), assinatura_removida_por=request.user)

    remover_assinatura.short_description = "Remove assinatura dos documentos selecionados"

    def save_model(self, request, obj, form, change):
        if not obj.criado_por:
            obj.criado_por = request.user
        super(DocTeste, self).save_model(request, obj, form, change)
