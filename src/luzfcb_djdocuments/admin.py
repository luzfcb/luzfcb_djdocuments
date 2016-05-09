# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from . import models
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html


@admin.register(models.Documento)
class DocumentoAdmin(SimpleHistoryAdmin):

    def get_queryset(self, request):
        qs = self.model.admin_objects.get_queryset()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    # form = DocumentoEditarForm
    list_display = (
        # 'criado_em', 'criado_por', 'versao_numero', 'assinatura_hash', 'visualizar_versao'
        'identificador_documento', 'pk', 'versao_numero', 'identificador_versao', 'visualizar_versao', 'eh_template',
        'esta_assinado', 'assinatura_hash', 'criado_por', 'criado_em', 'visualizar_titulo',
        'modificado_em',
        'tipo_documento',
        # 'tipo_documento__titulo',
        # 'tipo_documento__descricao',
        'template_descricao',
        'modificado_por', 'revertido_em', 'revertido_por',
        'revertido_da_versao', 'esta_ativo', 'esta_bloqueado',
        'assinado_em', 'assinado_por', 'assinatura_removida_em', 'assinatura_removida_por',

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

    def visualizar_titulo(self, obj):
        return remover_tags_html(obj.titulo)

    visualizar_titulo.short_description = "Título"

    def remover_assinatura(self, request, queryset):
        queryset.update(assinatura_hash='', esta_assinado=False, assinado_em=None, assinado_por=None,
                        assinatura_removida_em=timezone.now(), assinatura_removida_por=request.user)

    remover_assinatura.short_description = "Remove assinatura dos documentos selecionados"

    def save_model(self, request, obj, form, change):
        if not obj.criado_por:
            obj.criado_por = request.user
        super(DocumentoAdmin, self).save_model(request, obj, form, change)


@admin.register(models.DocumentoTemplate)
class DocumentoTemplateAdmin(DocumentoAdmin):
    objects = models.DocumentoTemplateManager()
    readonly_fields = DocumentoAdmin.readonly_fields + ('eh_template',)

    # def get_form(self, request, obj=None, *args, **kwargs):
    #     form = super(DocumentoTemplateAdmin, self).get_form(request, *args, **kwargs)
    #     # Initial values
    #     form.base_fields['eh_template'].initial = True
    #     if obj and obj.eh_template:
    #         form.base_fields['eh_template'].initial = obj.eh_template
    #     return form

    def save_model(self, request, obj, form, change):
        if not obj.eh_template:
            obj.eh_template = True
        super(DocumentoTemplateAdmin, self).save_model(request, obj, form, change)


@admin.register(models.TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    pass
