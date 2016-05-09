# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.views import generic

from ..models import DocumentoTemplate


class DocumentoTemplateDashboard(generic.TemplateView):
    template_name = 'luzfcb_djdocuments/documento_template_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentoTemplateDashboard, self).get_context_data(**kwargs)
        quantidade_documentos_cadastrados = None
        quantidade_meus_documentos = None
        if self.request.user.is_authenticated():
            quantidade_meus_documentos = DocumentoTemplate.objects.all().filter(criado_por=self.request.user).count()
            quantidade_documentos_cadastrados = DocumentoTemplate.objects.all().count()
        context['quantidade_documentos_cadastrados'] = quantidade_documentos_cadastrados
        context['quantidade_meus_documentos'] = quantidade_meus_documentos
        return context


class DocumentoTemplateListView(generic.ListView):
    template_name = 'luzfcb_djdocuments/documento_list.html'
    model = DocumentoTemplate

    def render_to_response(self, context, **response_kwargs):
        rend = super(DocumentoTemplateListView, self).render_to_response(context, **response_kwargs)
        return rend

    def get_queryset(self):
        qs = super(DocumentoTemplateListView, self).get_queryset()
        # if self.request.user.is_authenticated():

        # qs = qs.filter(
        #     (
        #         Q(criado_por_id=self.request.user.pk) | Q(assinado_por_id=self.request.user.pk)
        #     )
        # ).order_by('assinado_por')

        return qs
