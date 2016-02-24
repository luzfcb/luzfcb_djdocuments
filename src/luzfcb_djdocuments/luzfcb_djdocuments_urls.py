# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from .settings import DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD

from . import views

urlpatterns = [
    # url(r'^$',
    # TemplateView.as_view(template_name="luzfcb_djdocuments/ckeditor_sharedspaces_fakePaperPage.html"),
    # name='dashboard'
    # ),
    url(r'^$',
        views.DocumentoDashboardView.as_view(),
        name='dashboard'
        ),
    url(r'^list/$',
        views.DocumentoListView.as_view(),
        name='list'
        ),
    # url(r'^create/$',
    #     DocumentoCreateView.as_view(),
    #     name='create'
    #     ),
    url(r'^d/create/$',
        views.DocumentoCreateView.as_view(),
        name='create'
        ),
    url(r'^detail/(?P<pk>\d+)/$',
        views.DocumentoDetailView.as_view(),
        name='detail'
        ),
    url(r'^update/(?P<pk>\d+)/$',
        views.DocumentoUpdateView.as_view(),
        name='update'
        ),
    url(r'^update2/(?P<pk>\d+)/$',
        views.AjaxUpdateTesteApagar.as_view(),
        name='update2'
        ),
    url(r'^history/(?P<pk>\d+)/$',
        views.DocumentoHistoryView.as_view(),
        name='history'
        ),
    url(r'^revert/(?P<pk>\d+)/$',
        views.DocumentoRevertView.as_view(),
        name='revert'
        ),
    url(r'^close/$',
        views.CloseView.as_view(),
        name='close'
        ),
    url(r'^assinar/(?P<pk>\d+)/$',
        views.AssinarDocumentoView.as_view(),
        name='assinar'
        ),
    url(r'^validar/$',
        views.DocumentoValidacaoView.as_view(),
        name='validar'
        ),
    url(r'^validar/visualizar/(?P<pk>\d+)/$',
        views.DocumentoDetailValidarView.as_view(),
        name='validar-detail'
        ),
    url(r'^imprimir/(?P<pk>\d+)/$',
        views.ImprimirView.as_view(),
        name='imprimir'
        ),
    url(r'^pdf-file/$',
        views.PDFViewer.as_view(),
        name='pdf_view'
        ),

]

if DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD:
    urlpatterns += [
        url(r'^all$',
            views.DocumentoGeneralDashboardView.as_view(),
            name='dashboard_general'
            ),
    ]
