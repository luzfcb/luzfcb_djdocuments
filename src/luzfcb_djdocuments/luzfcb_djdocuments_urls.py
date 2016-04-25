# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

import luzfcb_djdocuments.views.autocompletes
from .settings import DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD
from .views import documentos as documentos_views
from .views import documento_template

urlpatterns = [
    # url(r'^$',
    # TemplateView.as_view(template_name="luzfcb_djdocuments/ckeditor_sharedspaces_fakePaperPage.html"),
    # name='dashboard'
    # ),
    url(r'^$',
        documentos_views.DocumentoDashboardView.as_view(),
        name='dashboard'
        ),
    url(r'^list/$',
        documentos_views.DocumentoListView.as_view(),
        name='list'
        ),
    # url(r'^create/$',
    #     DocumentoCreateView.as_view(),
    #     name='create'
    #     ),
    url(r'^d/create/$',
        documentos_views.DocumentoCriar.as_view(),
        # documentos_views.criar_documento,
        name='create'
        ),
    url(r'^detail/(?P<pk>\d+)/$',
        documentos_views.DocumentoDetailView.as_view(),
        name='detail'
        ),
    url(r'^update2/(?P<pk>\d+)/$',
        documentos_views.DocumentoEditor.as_view(),
        name='editar'
        ),
    url(r'^history/(?P<pk>\d+)/$',
        documentos_views.DocumentoHistoryView.as_view(),
        name='history'
        ),
    url(r'^revert/(?P<pk>\d+)/$',
        documentos_views.DocumentoRevertView.as_view(),
        name='revert'
        ),
    url(r'^close/$',
        documentos_views.CloseView.as_view(),
        name='close'
        ),
    url(r'^assinar/(?P<pk>\d+)/$',
        documentos_views.AssinarDocumentoView.as_view(),
        name='assinar'
        ),
    url(r'^validar/$',
        documentos_views.DocumentoValidacaoView.as_view(),
        name='validar'
        ),
    url(r'^validar/visualizar/(?P<pk>\d+)/$',
        documentos_views.DocumentoDetailValidarView.as_view(),
        name='validar-detail'
        ),
    url(r'^pdf-file/$',
        documentos_views.PDFViewer.as_view(),
        name='pdf_view'
        ),
    url(r'^user-autocomplete/$',
        luzfcb_djdocuments.views.autocompletes.UserAutocomplete.as_view(),
        name='user-autocomplete'
        ),
    url(r'^documento-criarautocomplete/$',
        luzfcb_djdocuments.views.autocompletes.DocumentoCriarAutocomplete.as_view(),
        name='documentocriar-autocomplete'
        ),
    url(r'^pdf/$',
        luzfcb_djdocuments.views.documentos.TestePDF.as_view(),
        name='pdf-teste'
        ),
]

if DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD:
    urlpatterns += [
        url(r'^all$',
            documentos_views.DocumentoGeneralDashboardView.as_view(),
            name='dashboard_general'
            ),
    ]

urlpatterns = urlpatterns + [
    url(r'^t/list/$',
        documento_template.DocumentoTemplateListView.as_view(),
        name='template_list'
        ),
    url(r'^t/$',
        documento_template.DocumentoTemplateDashboard.as_view(),
        name='template_dashboard'
        ),
]
