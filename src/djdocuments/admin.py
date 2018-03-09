# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from . import models
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
from .utils import admin_method_attributes


@admin.register(models.Documento)
class DocumentoAdmin(SimpleHistoryAdmin):
    manager_field = 'admin_objects'  # utilize para caso voce use mais de um manager no model
    ordering = ()

    search_fields = ('id', 'pk_uuid', 'assunto')

    def get_queryset(self, request):
        qs = getattr(self.model, self.manager_field).get_queryset()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    list_filter = ['eh_modelo', 'esta_assinado']
    # form = DocumentoEditarForm
    list_display = (
        # 'criado_em', 'criado_por', 'versao_numero', 'visualizar_versao'

        'identificador_documento', 'versao_numero', 'identificador_versao', 'pk', 'pk_uuid', 'assunto',
        'visualizar_versao', 'esta_assinado', 'eh_modelo', 'esta_ativo', 'eh_modelo_padrao', 'modelo_descricao',
        # 'grupo_dono',
        'editar_documento',
        'visualizar_documento', 'gerar_e_visualizar_pdf',
        # 'esta_assinado', 'assinatura_hash', 'criado_por', 'criado_em',
        # 'visualizar_titulo',
        # 'modificado_em',
        # 'tipo_documento',

        # 'tipo_documento__titulo',
        # 'tipo_documento__descricao',

        # 'modelo_descricao',
        # 'modificado_por', 'revertido_em', 'revertido_por',
        # 'revertido_da_versao',
        # 'assinado_em', 'assinado_por', 'assinatura_removida_em', 'assinatura_removida_por',

    )

    readonly_fields = (
        # 'identificador_versao',
        # 'assinatura_hash', 'assinado_em', 'assinado_por', 'criado_em', 'criado_por', 'modificado_em', 'modificado_por',
        # 'revertido_em',
        # 'revertido_por', 'revertido_da_versao',
        'pk_uuid',
        'esta_assinado',
        'rodape_qr_validacao',
        'conteudo_assinaturas',

    )
    # readonly_fields = ('criado_em', 'criado_por', 'modificado_em', 'modificado_por', 'revertido_em', 'revertido_por',
    #                    'revertido_da_versao',
    #                    )
    actions = [
        'reativar_documentos',
        'desativar_documentos',
        'remover_assinatura',
    ]

    def visualizar_versao(self, obj):
        url_triplet = self.admin_site.name, self.model._meta.app_label, self.model._meta.model_name
        history_url = reverse('%s:%s_%s_history' % url_triplet,
                              args=(obj.pk,))
        html = format_html('<a href="{}">{}</a>'.format(history_url, 'Versões'))
        return html

    visualizar_versao.allow_tags = True
    visualizar_versao.short_description = "Visualizar Versões"

    def editar_documento(self, obj):
        if obj.eh_modelo:
            url_edicao = reverse('documentos:editar-modelo', kwargs={'slug': obj.pk_uuid})
        else:
            url_edicao = reverse('documentos:editar', kwargs={'slug': obj.pk_uuid})
        return format_html('<a href="{}" target="_blank">{}</a>'.format(url_edicao, 'Editar'))

    editar_documento.short_description = 'Editar no Editor'

    def visualizar_documento(self, obj):
        if obj.eh_modelo:
            url_visualizacao = reverse('documentos:validar-detail-modelo', kwargs={'slug': obj.pk_uuid})
        else:
            url_visualizacao = reverse('documentos:validar-detail', kwargs={'slug': obj.pk_uuid})
        return format_html('<a href="{}" target="_blank">{}</a>'.format(url_visualizacao, 'Visualizar'))

    visualizar_documento.short_description = 'Visualizar Documento'

    def gerar_e_visualizar_pdf(self, obj):
        if obj.eh_modelo:
            url_visualizacao = reverse('documentos:validar-detail-modelo-pdf', kwargs={'slug': obj.pk_uuid})
        else:
            url_visualizacao = reverse('documentos:validar_detail_pdf', kwargs={'slug': obj.pk_uuid})
        return format_html('<a href="{}" target="_blank">{}</a>'.format(url_visualizacao, 'Gerar PDF'))

    gerar_e_visualizar_pdf.short_description = 'Gerar PDF'

    # def visualizar_titulo(self, obj):
    #     return remover_tags_html(obj.titulo)
    #
    # visualizar_titulo.short_description = "Título"

    @admin_method_attributes(short_description="Remove assinatura dos documentos selecionados")
    def remover_assinatura(self, request, queryset):
        with transaction.atomic():
            for obj in queryset:
                obj.assinaturas.update(ativo=False)
            queryset.update(assinatura_hash='', esta_assinado=False, assinado_em=None, assinado_por=None,
                            assinatura_removida_em=timezone.now(), assinatura_removida_por=request.user)

    @admin_method_attributes(
        short_description="Desativa o documento e suas respectivas assinaturas de todos os documentos selecionados")
    def desativar_documentos(self, request, queryset):
        with transaction.atomic():
            for obj in queryset:
                obj.assinaturas.update(ativo=False)
            queryset.update(esta_ativo=False)
            print('passou aqui')

    @admin_method_attributes(short_description="Reativar documento(s) e suas respectivas assinaturas")
    def reativar_documentos(self, request, queryset):
        with transaction.atomic():
            qs = queryset.filter(esta_ativo=False)
            for obj in qs:
                assinaturas = obj.assinaturas.order_by('grupo_assinante_id', '-cadastrado_em').distinct(
                    'grupo_assinante_id').values(
                    'cadastrado_em', 'pk', 'grupo_assinante_id')
                assinaturas.update(ativo=True)
            queryset.update(esta_ativo=True)

    def save_model(self, request, obj, form, change):
        if not obj.criado_por:
            obj.criado_por = request.user
        super(DocumentoAdmin, self).save_model(request, obj, form, change)


# @admin.register(models.DocumentoTemplate)
# class DocumentoTemplateAdmin(DocumentoAdmin):
#     readonly_fields = DocumentoAdmin.readonly_fields + ('eh_modelo',)
#
#     # def get_form(self, request, obj=None, *args, **kwargs):
#     #     form = super(DocumentoTemplateAdmin, self).get_form(request, *args, **kwargs)
#     #     # Initial values
#     #     form.base_fields['eh_modelo'].initial = True
#     #     if obj and obj.eh_modelo:
#     #         form.base_fields['eh_modelo'].initial = obj.eh_modelo
#     #     return form
#
#     def save_model(self, request, obj, form, change):
#         if not obj.eh_modelo:
#             obj.eh_modelo = True
#         super(DocumentoTemplateAdmin, self).save_model(request, obj, form, change)


@admin.register(models.TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    search_fields = ('id', 'titulo', 'descricao')
    list_display = ('id', 'titulo', 'descricao')


@admin.register(models.Assinatura)
class AssinaturaDocumentoAdmin(admin.ModelAdmin):
    search_fields = (
        # 'documento_pk_uuid',
        'documento_id',
    )
    list_display = (
        'documento',
        'grupo_assinante_nome',
        'assinado_nome',
        'versao_documento',
        'hash_assinatura',
        'assinado_em',
        'esta_assinado',
        'ativo',
        'documento_eh_modelo',

    )

    def visualizar_pk_uuid(self, obj):
        return obj.documento.pk_uuid

    def documento_eh_modelo(self, obj):
        return obj.documento.eh_modelo

    visualizar_pk_uuid.short_description = 'PK_UUID'
    readonly_fields = (
        'cadastrado_por',
        'nome_cadastrado_por',
        'assinado_por',
        'grupo_assinante',
        'grupo_assinante_nome',
        'documento',
        'visualizar_pk_uuid',
        'assinado_nome',
        'versao_documento',
        'hash_assinatura',
        'assinado_em',
        'esta_assinado',
        'nome_excluido_por',
        'documento_eh_modelo',
    )

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        try:
            queryset, use_distinct = super(AssinaturaDocumentoAdmin, self).get_search_results(request, queryset, search_term)
        except TypeError:
            try:
                search_term_as_int = int(search_term)
            except ValueError:
                pass
            else:
                queryset = self.model.objects.filter(documento_id=search_term_as_int)
        return queryset, use_distinct


@admin.register(models.PDFDocument)
class PDFDocumentAdmin(SimpleHistoryAdmin):
    pass
