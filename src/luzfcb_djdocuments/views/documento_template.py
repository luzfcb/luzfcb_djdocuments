# -*- coding: utf-8 -*-
from django.views import generic

from ..models import DocumentoTemplate


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
