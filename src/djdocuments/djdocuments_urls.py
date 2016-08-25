# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import documentos as documentos_views
from .views import autocompletes

# from .views import documento_template

urlpatterns = [
    url(r'^$',
        login_required(documentos_views.DocumentoPainelGeralView.as_view()),
        name='dashboard'
        ),
    url(r'^g/$',
        login_required(documentos_views.DocumentoPainelGeralPorGrupoView.as_view()),
        name='dashboard-por-grupo'
        ),
    url(r'^list/$',
        login_required(documentos_views.DocumentoListView.as_view()),
        name='list'
        ),
    url(r'^d/create/(?P<group_pk>\d+)/$',
        login_required(documentos_views.DocumentoCriarParaGrupo.as_view()),
        name='create-para-grupo'
        ),
    url(r'^d/create/$',
        login_required(documentos_views.DocumentoCriar.as_view()),
        name='create'
        ),
    url(r'^d/validar/$',
        documentos_views.DocumentoValidacaoView.as_view(),
        name='validar'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/validar-detail/pdf$',
        documentos_views.PrintPDFDocumentoDetailValidarView.as_view(),
        name='validar_detail_pdf'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/validar-detail/$',
        documentos_views.DocumentoDetailValidarView.as_view(),
        name='validar-detail'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/editar/$',
        login_required(documentos_views.DocumentoEditor.as_view()),
        name='editar'
        ),
    url(r'^d/m/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/editar/$',
        login_required(documentos_views.DocumentoEditorModelo.as_view()),
        name='editar-modelo'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/assinar/$',
        login_required(documentos_views.AssinarDocumentoView.as_view()),
        name='assinar'
        ),
    url(
        r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/assinar/(?P<group_id>\d+)/$',
        # noqa
        login_required(documentos_views.AssinarDocumentoView.as_view()),
        name='assinar_por_grupo'
    ),
    url(
        r'^d/(?P<document_slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/remover/(?P<pk>\d+)/$',
        # noqa
        login_required(documentos_views.AssinaturaDeleteView.as_view()),
        name='remover_assinatura'
    ),
    url(r'^d/assinaturas-pendentes/$',
        login_required(documentos_views.AssinaturasPendentesGrupo.as_view()),
        name='pendentes'
        ),
    url(r'^d/documentos-prontos-para-finalizar/$',
        login_required(documentos_views.DocumentosProntosParaFinalizarGrupo.as_view()),
        name='documentos_prontos_para_finalizar'
        ),
    url(r'^d/documentos-assinados/$',
        login_required(documentos_views.DocumentosAssinadosGrupo.as_view()),
        name='assinados'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/$',
        login_required(documentos_views.DocumentoAssinaturasListView.as_view()),
        name='assinaturas'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/assinaturas/finalizar/$',
        login_required(documentos_views.FinalizarDocumentoFormView.as_view()),
        name='finalizar_assinatura'
        ),
    url(r'^d/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/adicionar_assinantes/$',
        login_required(documentos_views.AdicionarAssinantes.as_view()),
        name='adicionar_assinantes'
        ),
    url(r'^d/create-template/$',
        login_required(documentos_views.DocumentoModeloCriar.as_view()),
        # documentos_views.criar_documento,
        name='create-template'
        ),
    url(r'^users-autocomplete/$',
        login_required(autocompletes.UserAutocomplete.as_view()),
        name='user-autocomplete'
        ),
    url(r'^users-by-group-autocomplete/$',
        login_required(autocompletes.UsersByGroupAutocomplete.as_view()),
        name='user-by-group-autocomplete'
        ),
    url(r'^grupos-autocomplete/$',
        login_required(autocompletes.GruposDoUsuarioAutoComplete.as_view()),
        name='grupos-autocomplete'
        ),
    url(r'^grupos-autocomplete/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        login_required(autocompletes.GruposAssinantesDoDocumentoAutoComplete.as_view()),
        name='grupos_assinantes_do_documento_autocomplete'
        ),
    url(
        r'^grupos-nao-assintantes-autocomplete/(?P<slug>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        login_required(autocompletes.GrupoAindaNaoAssinantesDoDocumentoAutoComplete.as_view()),
        name='grupos_ainda_nao_assinantes_do_documento_autocomplete'
    ),

    url(r'^documento-criarautocomplete/$',
        login_required(autocompletes.DocumentoCriarAutocomplete.as_view()),
        name='documentocriar-autocomplete'
        ),

]
