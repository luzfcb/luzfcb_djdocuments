# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from .views import autocompletes

from .settings import DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD
from .views import documentos as documentos_views

# from .views import documento_template

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
    url(r'^d/create/$',
        documentos_views.DocumentoCriar.as_view(),
        # documentos_views.criar_documento,
        name='create'
        ),
    url(r'^editar/(?P<pk>\d+)/$',
        documentos_views.DocumentoEditor.as_view(),
        name='editar'
        ),
    url(r'^d/create-template/$',
        documentos_views.DocumentoModeloCriar.as_view(),
        # documentos_views.criar_documento,
        name='create-template'
        ),
    url(r'^user-autocomplete/$',
        autocompletes.UserAutocomplete.as_view(),
        name='user-autocomplete'
        ),
    url(r'^documento-criarautocomplete/$',
        autocompletes.DocumentoCriarAutocomplete.as_view(),
        name='documentocriar-autocomplete'
        ),

]
