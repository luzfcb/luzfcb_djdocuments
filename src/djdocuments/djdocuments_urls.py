# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from .settings import DJANGO_DOCUMENTOS_ENABLE_GENERAL_DASHBOARD
from .views import documentos as documentos_views
from .views import autocompletes

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
        name='create'
        ),
    url(r'^d/validar/$',
        documentos_views.DocumentoValidacaoView.as_view(),
        name='validar'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/validar-detail/$',
        documentos_views.DocumentoDetailValidarView.as_view(),
        name='validar-detail'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/editar/$',
        documentos_views.DocumentoEditor.as_view(),
        name='editar'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/assinar/$',
        documentos_views.AssinarDocumentoView.as_view(),
        name='assinar'
        ),
    url(
        r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/assinar/(?P<group_id>[0-9]+)/$',
        # noqa
        documentos_views.AssinarDocumentoView.as_view(),
        name='assinar_por_grupo'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/$',
        documentos_views.DocumentoAssinaturasListView.as_view(),
        name='assinaturas'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/adicionar_assinantes/$',
        documentos_views.AdicionarAssinantes.as_view(),
        name='adicionar_assinantes'
        ),
    url(r'^d/create-template/$',
        documentos_views.DocumentoModeloCriar.as_view(),
        # documentos_views.criar_documento,
        name='create-template'
        ),
    url(r'^users-autocomplete/$',
        autocompletes.UserAutocomplete.as_view(),
        name='user-autocomplete'
        ),
    url(r'^users-by-group-autocomplete/$',
        autocompletes.UsersByGroupAutocomplete.as_view(),
        name='user-by-group-autocomplete'
        ),
    url(r'^grupos-autocomplete/$',
        autocompletes.GruposDoUsuarioAutoComplete.as_view(),
        name='grupos-autocomplete'
        ),
    url(r'^grupos-autocomplete/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        autocompletes.GruposAssinantesDoDocumentoAutoComplete.as_view(),
        name='grupos-assinantes-do-documento'
        ),

    url(r'^documento-criarautocomplete/$',
        autocompletes.DocumentoCriarAutocomplete.as_view(),
        name='documentocriar-autocomplete'
        ),

]
