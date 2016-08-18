# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from luzfcb_dj_simplelock.views import LuzfcbLockMixin
from wkhtmltopdf.views import PDFRenderMixin

from ..backends import DjDocumentsBackendMixin
from ..forms import (
    CriarDocumentoForm,
    CriarDocumentoParaGrupoForm,
    CriarModeloDocumentoForm,
    DocumentoEditarForm,
    DocumetoValidarForm,
    FinalizarDocumentoForm,
    create_form_class_adicionar_assinantes,
    create_form_class_assinar
)
from ..models import Assinatura, Documento
from .mixins import (
    AjaxFormPostMixin,
    AuditavelViewMixin,
    DocumentoAssinadoRedirectMixin,
    FormActionViewMixin,
    NextURLMixin,
    PopupMixin,
    QRCodeValidacaoMixin,
    SingleDocumentObjectMixin,
    SingleGroupObjectMixin,
    VinculateMixin
)

logger = logging.getLogger('djdocuments')
logger.setLevel(logging.INFO)

USER_MODEL = get_user_model()


class DocumentoDashboardView(generic.TemplateView):
    template_name = 'luzfcb_djdocuments/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentoDashboardView, self).get_context_data(**kwargs)
        quantidade_documentos_cadastrados = None
        quantidade_meus_documentos = None
        if self.request.user.is_authenticated():
            quantidade_meus_documentos = Documento.objects.all().filter(criado_por=self.request.user).count()
            quantidade_documentos_cadastrados = Documento.objects.all().count()
        context['quantidade_documentos_cadastrados'] = quantidade_documentos_cadastrados
        context['quantidade_meus_documentos'] = quantidade_meus_documentos
        return context


class DocumentoListView(generic.ListView):
    template_name = 'luzfcb_djdocuments/documento_list.html'
    model = Documento
    paginate_by = 5

    def render_to_response(self, context, **response_kwargs):
        rend = super(DocumentoListView, self).render_to_response(context, **response_kwargs)
        return rend

    def get_queryset(self):
        qs = super(DocumentoListView, self).get_queryset()
        # if self.request.user.is_authenticated():

        # qs = qs.filter(
        #     (
        #         Q(criado_por_id=self.request.user.pk) | Q(assinado_por_id=self.request.user.pk)
        #     )
        # ).order_by('assinado_por')

        return qs


class DocumentoEditor(AjaxFormPostMixin,
                      DocumentoAssinadoRedirectMixin,
                      AuditavelViewMixin,
                      NextURLMixin,
                      PopupMixin,
                      LuzfcbLockMixin,
                      generic.UpdateView):
    detail_view_named_url = 'documentos:detail'
    document_json_fields = ('titulo', 'document_number', 'document_version_number', 'identificador_versao')
    template_name = 'luzfcb_djdocuments/editor/documento_editor.html'
    # template_name = 'luzfcb_djdocuments/documento_update.html'
    lock_revalidated_at_every_x_seconds = 3
    model = Documento
    slug_field = 'pk_uuid'
    prefix = 'document'
    # form_class = DocumentoFormCreate
    form_class = DocumentoEditarForm
    success_url = reverse_lazy('documentos:list')

    def get_context_data(self, **kwargs):
        context = super(DocumentoEditor, self).get_context_data(**kwargs)
        context['url_para_assinar'] = reverse_lazy('documentos:assinar_por_grupo',
                                                   kwargs={'slug': self.object.pk_uuid,
                                                           'group_id': self.object.grupo_dono.pk})
        return context

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).dispatch(request, *args, **kwargs)

    def get_lock_url_to_redirect_if_locked(self):
        return reverse('documentos:validar-detail', kwargs={'slug': self.object.pk_uuid})

    def form_valid(self, form):
        status, mensagem = self.object.pode_editar(usuario_atual=self.request.user)
        if not status:
            raise PermissionDenied(mensagem)
        response = super(DocumentoEditor, self).form_valid(form)

        return response

        # success_url = None

    def get(self, request, *args, **kwargs):
        response = super(DocumentoEditor, self).get(request, *args, **kwargs)

        status, mensagem = self.object.pode_editar(usuario_atual=self.request.user)
        if not status:
            raise PermissionDenied(mensagem)
        return response

    def post(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).post(request, *args, **kwargs)


def create_document_from_document_template(current_user, grupo, documento_template, assunto):
    # template_documento = Documento.objects.get(pk=documento_template.pk)

    document_kwargs = {
        'cabecalho': documento_template.cabecalho,
        'titulo': documento_template.titulo,
        'conteudo': documento_template.conteudo,
        'rodape': documento_template.rodape,
        'tipo_documento': documento_template.tipo_documento,
        'criado_por': current_user,
        'modificado_por': current_user,
        'grupo_dono': grupo,
        'assunto': assunto,
    }

    documento_novo = Documento(**document_kwargs)
    documento_novo.save()
    documento_novo.adicionar_grupos_assinantes(grupo, current_user)

    return documento_novo


class DocumentoCriar(VinculateMixin, FormActionViewMixin, DjDocumentsBackendMixin, generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_create2.html'
    form_class = CriarDocumentoForm
    default_selected_document_template_pk = None
    document_slug_url_kwarg = 'document_pk'
    form_action = reverse_lazy('documentos:create')

    def get_form_kwargs(self):
        kwargs = super(DocumentoCriar, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.get_vinculate_parameters()
        modelo_documento = form.cleaned_data['modelo_documento']
        grupo = form.cleaned_data['grupo']
        assunto = form.cleaned_data['assunto']
        print('{} - grupo: {}'.format(self.__class__.__name__, grupo))
        documento_novo = create_document_from_document_template(current_user=self.request.user,
                                                                grupo=grupo,
                                                                documento_template=modelo_documento,
                                                                assunto=assunto)
        # vinculate_view_name = self.request.GET.get(self.vinculate_view_field, None)
        # vinculate_value = self.request.GET.get(self.vinculate_value_field, None)

        if self.vinculate_view_name and self.vinculate_value:
            viculate_url = reverse(self.vinculate_view_name, kwargs={'document_pk': documento_novo.pk,
                                                                     'pk': self.vinculate_value})
            return redirect(viculate_url, permanent=True)
        else:
            editar_url = reverse('documentos:editar', kwargs={'slug': documento_novo.pk_uuid})
            return redirect(editar_url, permanent=True)


class DocumentoCriarParaGrupo(SingleGroupObjectMixin, DocumentoCriar):
    form_class = CriarDocumentoParaGrupoForm

    def get(self, request, *args, **kwargs):
        response = super(DocumentoCriarParaGrupo, self).get(request, *args, **kwargs)
        status, mensagem = self.djdocuments_backend.pode_criar_documento_para_grupo(usuario=self.request.user,
                                                                                    grupo=self.group_object)

        if not status:
            return render(request=request, template_name='luzfcb_djdocuments/erros/erro_403.html',
                          context={'mensagem': mensagem})
            # raise PermissionDenied(mensagem)
        return response

    def get_form_action(self):
        return reverse('documentos:create-para-grupo',
                       kwargs={'group_pk': self.group_object.pk})

    def get_form_kwargs(self):
        kwargs = super(DocumentoCriarParaGrupo, self).get_form_kwargs()
        if self.group_object:
            grupo_escolhido_queryset = self.group_model.objects.filter(pk=self.group_object.pk)
            kwargs['grupo_escolhido_queryset'] = grupo_escolhido_queryset
            kwargs['grupo_escolhido'] = self.group_object
        return kwargs

    def get_initial(self):
        initial = super(DocumentoCriarParaGrupo, self).get_initial()
        initial['grupo'] = self.group_object
        return initial

    def form_valid(self, form):
        form = super(DocumentoCriarParaGrupo, self).form_valid(form)
        return form


class DocumentoModeloCriar(DocumentoCriar):
    form_class = CriarModeloDocumentoForm


class VincularDocumentoBaseView(SingleDocumentObjectMixin, SingleObjectMixin, generic.View):
    model = None
    documents_field_name = None

    document_edit_named_view = 'documentos:editar'

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(VincularDocumentoBaseView, self).dispatch(request, *args, **kwargs)

    def get_documents_field_name(self):
        if self.documents_field_name is None:
            raise ImproperlyConfigured(
                '{0} is missing an documents_field_name. '
                'Define '
                '{0}.documents_field_name or override '
                '{0}.get_documents_field_name(). '.format(
                    self.__class__.__name__)
            )
        return self.documents_field_name

    def get(self, request, *args, **kwargs):
        self.documents_field_name = self.get_documents_field_name()

        self.object = self.get_object()  # obtenho tarefa
        self.document_object = self.get_document_object()  # obtenho documento

        self.vinculate()

        editar_url = reverse(self.document_edit_named_view, kwargs={'slug': self.document_object.pk_uuid})
        return redirect(editar_url, permanent=True)

    def vinculate(self):
        document_field = getattr(self.object, self.documents_field_name)
        with transaction.atomic():
            if not document_field.filter(id=self.document_object.pk).exists():
                try:
                    document_field.add(self.document_object)
                except IntegrityError as e:
                    logger.error(e)
                else:
                    self.object.save()
                    # logger.info('')
                    return True
        return False


class FinalizarDocumentoFormView(SingleDocumentObjectMixin, generic.FormView):
    form_class = FinalizarDocumentoForm
    http_method_names = ['post']

    def get_form_kwargs(self):
        kwargs = super(FinalizarDocumentoFormView, self).get_form_kwargs()
        kwargs['current_logged_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # form.cleaned_data[]
        if self.document_object.pronto_para_finalizar:
            self.document_object.finalizar_documento(self.request.user)
        else:
            # raise PermissionDenied()
            return HttpResponseForbidden()

        return super(FinalizarDocumentoFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid})


class AssinaturasPendentesGrupo(DjDocumentsBackendMixin, generic.ListView):
    model = Assinatura
    template_name = 'luzfcb_djdocuments/assinaturas_pendentes_por_grupo.html'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(AssinaturasPendentesGrupo, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(AssinaturasPendentesGrupo, self).get_queryset()

        grupos = tuple(self.djdocuments_backend.get_grupos_usuario(self.request.user).values_list('id', flat=True))
        queryset = queryset.select_related('documento', 'grupo_assinante')

        queryset = queryset.filter(grupo_assinante_id__in=grupos, assinado_por=None, ativo=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AssinaturasPendentesGrupo, self).get_context_data(**kwargs)

        dados_processados = []
        for assinatura in self.object_list:
            pode_assinar = self.djdocuments_backend.pode_assinar(document=assinatura.documento,
                                                                 usuario=self.request.user,
                                                                 grupo_assinante=assinatura.grupo_assinante)
            dados = {
                'identificador_documento': assinatura.documento.identificador_documento,
                'assunto': assinatura.documento.assunto,
                'assinatura': assinatura,
                'esta_assinado': assinatura.esta_assinado,
                'pode_assinar': pode_assinar,
                'grupo_assinante_nome': self.djdocuments_backend.get_grupo_name(assinatura.grupo_assinante),
                'url_para_assinar': reverse_lazy('documentos:assinar_por_grupo',
                                                 kwargs={'slug': assinatura.documento.pk_uuid,
                                                         'group_id': assinatura.grupo_assinante.pk}),
                'url_remover_assinatura': reverse_lazy('documentos:remover_assinatura',
                                                       kwargs={'document_slug': assinatura.documento.pk_uuid,
                                                               'pk': assinatura.pk}),
                'url_para_visualizar': reverse('documentos:validar-detail',
                                               kwargs={'slug': assinatura.documento.pk_uuid})
            }
            dados_processados.append(dados)
        context['dados_processados'] = dados_processados
        return context


class DocumentosAssinadosGrupo(DjDocumentsBackendMixin, generic.ListView):
    model = Assinatura
    template_name = 'luzfcb_djdocuments/documentos_assinados_por_grupo.html'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentosAssinadosGrupo, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(DocumentosAssinadosGrupo, self).get_queryset()

        grupos = tuple(self.djdocuments_backend.get_grupos_usuario(self.request.user).values_list('id', flat=True))
        queryset = queryset.select_related('documento', 'grupo_assinante')

        queryset = queryset.filter(Q(grupo_assinante_id__in=grupos), ~Q(assinado_por=None), Q(ativo=True))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DocumentosAssinadosGrupo, self).get_context_data(**kwargs)

        dados_processados = []
        for assinatura in self.object_list:
            pode_assinar = self.djdocuments_backend.pode_assinar(document=assinatura.documento,
                                                                 usuario=self.request.user,
                                                                 grupo_assinante=assinatura.grupo_assinante)
            dados = {
                'identificador_documento': assinatura.documento.identificador_documento,
                'assunto': assinatura.documento.assunto,
                'assinatura': assinatura,
                'esta_assinado': assinatura.esta_assinado,
                'pode_assinar': pode_assinar,
                'grupo_assinante_nome': self.djdocuments_backend.get_grupo_name(assinatura.grupo_assinante),
                'url_para_assinar': reverse_lazy('documentos:assinar_por_grupo',
                                                 kwargs={'slug': assinatura.documento.pk_uuid,
                                                         'group_id': assinatura.grupo_assinante.pk}),
                'url_remover_assinatura': reverse_lazy('documentos:remover_assinatura',
                                                       kwargs={'document_slug': assinatura.documento.pk_uuid,
                                                               'pk': assinatura.pk}),
                'url_para_visualizar': reverse('documentos:validar-detail',
                                               kwargs={'slug': assinatura.documento.pk_uuid})
            }
            dados_processados.append(dados)
        context['dados_processados'] = dados_processados
        return context


class DocumentoAssinaturasListView(SingleDocumentObjectMixin, DjDocumentsBackendMixin, generic.ListView):
    model = Assinatura
    document_slug_field = 'pk_uuid'
    template_name = 'luzfcb_djdocuments/documento_assinaturas_pendentes.html'

    def get_queryset(self):
        queryset = self.document_object.assinaturas.select_related('grupo_assinante').all()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DocumentoAssinaturasListView, self).get_context_data(**kwargs)
        dados_processados = []
        for assinatura in self.object_list:
            pode_assinar = self.djdocuments_backend.pode_assinar(document=self.document_object,
                                                                 usuario=self.request.user,
                                                                 grupo_assinante=assinatura.grupo_assinante)
            dados = {
                'assinatura': assinatura,
                'esta_assinado': assinatura.esta_assinado,
                'pode_assinar': pode_assinar,
                'grupo_assinante_nome': self.djdocuments_backend.get_grupo_name(assinatura.grupo_assinante),
                'url_para_assinar': reverse_lazy('documentos:assinar_por_grupo',
                                                 kwargs={'slug': self.document_object.pk_uuid,
                                                         'group_id': assinatura.grupo_assinante.pk}),
                'url_remover_assinatura': reverse_lazy('documentos:remover_assinatura',
                                                       kwargs={'document_slug': self.document_object.pk_uuid,
                                                               'pk': assinatura.pk})
            }
            dados_processados.append(dados)
        context['dados_processados'] = dados_processados
        context['url_para_visualizar'] = reverse('documentos:validar-detail',
                                                 kwargs={'slug': self.document_object.pk_uuid})
        context['form'] = FinalizarDocumentoForm(current_logged_user=self.request.user)
        return context


class AdicionarAssinantes(SingleDocumentObjectMixin, DjDocumentsBackendMixin, generic.FormView):
    template_name = 'luzfcb_djdocuments/assinar_adicionar_assinantes.html'

    def get_form_class(self):
        return create_form_class_adicionar_assinantes(self.document_object)

    def get_form_kwargs(self):
        kwargs = super(AdicionarAssinantes, self).get_form_kwargs()
        grupos_ja_adicionados = self.document_object.grupos_assinates.all()
        grupo_para_adicionar_queryset = self.djdocuments_backend.get_grupos(
            excludes=grupos_ja_adicionados)
        kwargs.update({'grupo_para_adicionar_queryset': grupo_para_adicionar_queryset})
        return kwargs

    def form_valid(self, form):
        ret = super(AdicionarAssinantes, self).form_valid(form)

        grupo_para_adicionar = form.cleaned_data.get('grupo_para_adicionar')
        self.document_object.adicionar_grupos_assinantes(grupo_para_adicionar, self.request.user)
        return ret

    def get_success_url(self):
        return reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid})


class AssinarDocumentoView(DocumentoAssinadoRedirectMixin,
                           SingleDocumentObjectMixin,
                           DjDocumentsBackendMixin,
                           generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_assinar.html'
    # form_class = AssinarDocumentoForm
    model = Documento
    slug_field = 'pk_uuid'
    group_pk_url_kwarg = 'group_id'
    group_object = None

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get(self.group_pk_url_kwarg, None)
        if group_id:
            self.group_object = self.djdocuments_backend.get_grupo_model().objects.get(pk=group_id)
        ret = super(AssinarDocumentoView, self).get(request, *args, **kwargs)
        if self.group_object and self.djdocuments_backend.grupo_ja_assinou(self.document_object, self.request.user,
                                                                           grupo_assinante=self.group_object):
            logger.error(msg='Grupo ja assinou, redirecionando')
            return HttpResponseRedirect(
                reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid}))
        logger.error(msg='AssinarDocumentoView, retornou normal')
        return ret

    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(AssinarDocumentoView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return create_form_class_assinar(self.document_object)

    # def get_initial(self):
    #     initial = super(AssinarDocumentoView, self).get_initial()
    #     current_logged_user = self.request.user
    #     initial['current_logged_user'] = current_logged_user
    #     group_id = self.kwargs.get(self.group_pk_url_kwarg, None)
    #     initial['grupo_escolhido'] = None
    #     if group_id:
    #         initial['grupo_escolhido_pk'] = group_id
    #
    #     return initial

    def get_form_kwargs(self):
        kwargs = super(AssinarDocumentoView, self).get_form_kwargs()
        current_logged_user = self.request.user
        kwargs['current_logged_user'] = current_logged_user
        group_id = self.kwargs.get(self.group_pk_url_kwarg, None)
        # kwargs['grupo_escolhido'] = None
        if group_id:
            grupo_escolhido_queryset = self.document_object.grupos_assinates.all()
            if not grupo_escolhido_queryset:
                return HttpResponseNotFound('Grupo nao existe')
            kwargs['grupo_escolhido_queryset'] = grupo_escolhido_queryset
            kwargs['grupo_escolhido'] = self.document_object.grupos_assinates.get(id=group_id)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssinarDocumentoView, self).get_context_data(**kwargs)
        context['group_object'] = self.group_object
        return context

    def form_valid(self, form):
        ret = super(AssinarDocumentoView, self).form_valid(form)
        grupo_selecionado = form.cleaned_data['grupo']
        assinado_por = form.cleaned_data['assinado_por']
        senha = form.cleaned_data['password']
        self.document_object.assinar(grupo_assinante=grupo_selecionado, usuario_assinante=assinado_por, senha=senha)
        return ret

    def get_success_url(self):
        return reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid})


class DocumentoDetailView(NextURLMixin, PopupMixin, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_detail.html'
    # template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'
    model = Documento
    slug_field = 'pk_uuid'

    def get_queryset(self):
        qs = super(DocumentoDetailView, self).get_queryset()

        return qs

    def get_context_data(self, **kwargs):
        context = super(DocumentoDetailView, self).get_context_data(**kwargs)

        context['url_imprimir_pdf'] = reverse('documentos:validar_detail_pdf',
                                              kwargs={'slug': self.object.pk_uuid})
        # context['assinaturas'] = self.object.assinaturas.select_related('assinado_por').all()
        context['assinaturas'] = self.object.assinaturas.all()
        return context


class DocumentoDetailValidarView(QRCodeValidacaoMixin, DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'

    def render_to_response(self, context, **response_kwargs):
        return super(DocumentoDetailValidarView, self).render_to_response(context, **response_kwargs)


# class AssinaturaDeleteView(SingleDocumentObjectMixin, generic.DeleteView):
class AssinaturaDeleteView(generic.DeleteView):
    template_name = 'luzfcb_djdocuments/assinatura_confirm_delete.html'
    model = Assinatura
    document_slug_url_kwarg = 'document_slug'

    def get(self, request, *args, **kwargs):
        response = super(AssinaturaDeleteView, self).get(request, *args, **kwargs)
        status, mensagem = self.object.pode_remover_assinatura(self.request.user)
        if not status:
            raise PermissionDenied(mensagem)
        return response

    def get_context_data(self, **kwargs):
        context = super(AssinaturaDeleteView, self).get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('documentos:remover_assinatura',
                                              kwargs={'document_slug': self.object.documento.pk_uuid,
                                                      'pk': self.object.pk})
        return context

    def get_success_url(self):
        status, mensagem = self.object.pode_remover_assinatura(self.request.user)
        if not status:
            raise PermissionDenied(mensagem)
        return reverse('documentos:assinaturas', kwargs={'slug': self.object.documento.pk_uuid})


class PrintPDFDocumentoDetailValidarView(PDFRenderMixin, DocumentoDetailValidarView):
    pdf_template_name = 'luzfcb_djdocuments/pdf/corpo.html'
    pdf_header_template = 'luzfcb_djdocuments/pdf/cabecalho.html'
    pdf_footer_template = 'luzfcb_djdocuments/pdf/rodape.html'

    show_content_in_browser = True
    pdf_default_response_is_pdf = True
    cmd_options = {
        'print-media-type': True,

        # 'margin-top': '57.5mm',
        'margin-top': '61.5mm',
        # 'margin-left': '1.5mm',
        'margin-left': '1.0mm',
        # 'margin-right': '6.5mm',
        'margin-right': '3.5mm',
        # 'margin-bottom': '45.5mm',
        'margin-bottom': '47.5mm',
        # 'margin-bottom': '87.5mm',
        # 'page-width': '210mm',
        # 'page-height': '297mm',
        # 'viewport-size': '210mmX297mm',
        # 'orientation': 'Landscape',
        'page-size': 'A4'
    }

    def render_to_response(self, context, **response_kwargs):
        return super(PrintPDFDocumentoDetailValidarView, self).render_to_response(context, **response_kwargs)


class DocumentoValidacaoView(generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_validacao.html'
    model = Documento
    form_class = DocumetoValidarForm

    def __init__(self, *args, **kwargs):
        super(DocumentoValidacaoView, self).__init__(*args, **kwargs)
        self.documento_instance = None

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoValidacaoView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and request.GET and 'refresh_captcha' in request.GET:
            to_json_responce = dict()
            to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

            return JsonResponse(to_json_responce)
        return super(DocumentoValidacaoView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(DocumentoValidacaoView, self).get_initial()
        assinatura_hash = self.request.GET.get('h')
        if assinatura_hash:
            cleaned_hash = assinatura_hash.split('$')[-1]
            initial.update({
                'assinatura_hash': cleaned_hash
            })
        # initial.update({
        #     'codigo_crc': 'ABCD' * 4
        # })
        return initial

    def get_success_url(self):
        pk_uuid = self.get_object().pk_uuid
        return reverse_lazy('documentos:validar-detail', kwargs={'slug': pk_uuid})

    def get_object(self):
        return self.documento_instance

    def form_valid(self, form):
        self.documento_instance = form.documento
        return super(DocumentoValidacaoView, self).form_valid(form)
