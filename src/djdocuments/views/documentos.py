# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

import pyqrcode
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponseNotFound
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from luzfcb_dj_simplelock.views import LuzfcbLockMixin
from urlobject import URLObject
from wkhtmltopdf.views import PDFRenderMixin

from djdocuments.templatetags.luzfcb_djdocuments_tags import absolute_uri
from djdocuments.utils import get_grupo_assinante_backend
from djdocuments.utils.base64utils import png_as_base64_str
from ..forms import (CriarDocumentoForm, CriarModeloDocumentoForm, DocumentoEditarForm,
                     DocumetoValidarForm, create_form_class_assinar, FinalizarDocumento,
                     create_form_class_adicionar_assinantes)
from ..models import Assinatura, Documento
from ..utils.module_loading import get_real_user_model_class
from .auth_mixins import LoginRequiredMixin
from .mixins import (
    AjaxFormPostMixin,
    AuditavelViewMixin,
    DocumentoAssinadoRedirectMixin,
    NextURLMixin,
    PopupMixin,
    SingleDocumentObjectMixin,
    VinculateMixin,
    QRCodeValidacaoMixin)

logger = logging.getLogger(__name__)

USER_MODEL = get_real_user_model_class()


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


class DocumentoEditor(LoginRequiredMixin,
                      AjaxFormPostMixin,
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

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).dispatch(request, *args, **kwargs)

    def get_lock_url_to_redirect_if_locked(self):
        return reverse('documentos:detail', kwargs={'slug': self.object.pk_uuid})

    def form_valid(self, form):
        return super(DocumentoEditor, self).form_valid(form)

        # success_url = None

    def get(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).post(request, *args, **kwargs)


def create_from_template(current_user, documento_template, assunto):
    # template_documento = Documento.objects.get(pk=documento_template.pk)

    document_kwargs = {
        'cabecalho': documento_template.cabecalho,
        'titulo': documento_template.titulo,
        'conteudo': documento_template.conteudo,
        'rodape': documento_template.rodape,
        'tipo_documento': documento_template.tipo_documento,
        'criado_por': current_user,
        'modificado_por': current_user,
        'assunto': assunto,
    }

    documento_novo = Documento(**document_kwargs)
    documento_novo.save()

    return documento_novo


class DocumentoCriar(VinculateMixin, generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_create2.html'
    form_class = CriarDocumentoForm
    default_selected_document_template_pk = None
    document_slug_url_kwarg = 'document_pk'

    def get_form_kwargs(self):
        kwargs = super(DocumentoCriar, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.get_vinculate_parameters()
        modelo_documento = form.cleaned_data['modelo_documento']
        grupo = form.cleaned_data['grupo']
        assunto = form.cleaned_data['assunto']
        documento_novo = create_from_template(self.request.user, modelo_documento, assunto)
        # vinculate_view_name = self.request.GET.get(self.vinculate_view_field, None)
        # vinculate_value = self.request.GET.get(self.vinculate_value_field, None)

        if self.vinculate_view_name and self.vinculate_value:
            viculate_url = reverse(self.vinculate_view_name, kwargs={'document_pk': documento_novo.pk,
                                                                     'pk': self.vinculate_value})
            return redirect(viculate_url, permanent=True)
        else:
            editar_url = reverse('documentos:editar', kwargs={'slug': documento_novo.pk_uuid})
            return redirect(editar_url, permanent=True)

            # def get_initial(self):
            #     initial = super(DocumentoCriar, self).get_initial()
            #     default_document_template = self.get_default_selected_document_template_pk()
            #     if default_document_template:
            #         initial.update({'modelo_documento': default_document_template})
            #     else:
            #         document_pk_modelo = self.request.GET.get(self.document_slug_url_kwarg)
            #
            #         if document_pk_modelo:
            #             try:
            #
            #                 documento_modelo = Documento.objects.get(pk=document_pk_modelo)
            #             except Documento.DoesNotExist:
            #                 pass
            #             else:
            #                 print(documento_modelo)
            #                 initial.update({
            #                     'tipo_documento': documento_modelo.tipo_documento,
            #                     'modelo_documento': documento_modelo.pk
            #                 })
            #     return initial
            #
            # def get_default_selected_document_template_pk(self):
            #     return self.default_selected_document_template_pk


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


class DocumentoAssinaturasListView(SingleDocumentObjectMixin, generic.FormView, generic.ListView):
    model = Assinatura
    form_class = FinalizarDocumento
    document_slug_field = 'pk_uuid'
    template_name = 'luzfcb_djdocuments/assinaturas_pendentes.html'

    def get_form_kwargs(self):
        kwargs = super(DocumentoAssinaturasListView, self).get_form_kwargs()
        kwargs['current_logged_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # form.cleaned_data[]
        self.document_object.finalizar_documento(self.request.user)

        return super(DocumentoAssinaturasListView, self).form_valid(form)

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
        backend = get_grupo_assinante_backend()
        dados_processados = []
        for assinatura in self.object_list:
            pode_assinar = backend.pode_assinar(document=self.document_object,
                                                usuario=self.request.user,
                                                grupo_assinante=assinatura.grupo_assinante)
            dados = {
                'assinatura': assinatura,
                'esta_assinado': assinatura.esta_assinado,
                'pode_assinar': pode_assinar,
                'grupo_assinante_nome': backend.get_grupo_name(assinatura.grupo_assinante),
                'url_para_assinar': reverse_lazy('documentos:assinar_por_grupo',
                                                 kwargs={'slug': self.document_object.pk_uuid,
                                                         'group_id': assinatura.grupo_assinante.pk})
            }
            dados_processados.append(dados)
        context['dados_processados'] = dados_processados
        context['url_para_visualizar'] = reverse('documentos:validar-detail',
                                                 kwargs={'slug': self.document_object.pk_uuid})
        context['form'] = self.get_form()
        return context

    def get_success_url(self):
        return reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid})


class AdicionarAssinantes(SingleDocumentObjectMixin, generic.FormView):
    template_name = 'luzfcb_djdocuments/assinar_adicionar_assinantes.html'
    success_url = reverse_lazy('documentos:list')

    def get_form_class(self):
        return create_form_class_adicionar_assinantes(self.document_object)

    def get_form_kwargs(self):
        kwargs = super(AdicionarAssinantes, self).get_form_kwargs()
        grupos_ja_adicionados = self.document_object.grupos_assinates.all()
        grupo_para_adicionar_queryset = get_grupo_assinante_backend().get_grupos(
            excludes=grupos_ja_adicionados)
        kwargs.update({'grupo_para_adicionar_queryset': grupo_para_adicionar_queryset})
        return kwargs

    def form_valid(self, form):
        ret = super(AdicionarAssinantes, self).form_valid(form)

        grupo_para_adicionar = form.cleaned_data.get('grupo_para_adicionar')
        self.document_object.adicionar_grupos_assinantes(grupo_para_adicionar, self.request.user)
        return ret


class AssinarDocumentoView(DocumentoAssinadoRedirectMixin, SingleDocumentObjectMixin,
                           generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_assinar.html'
    # form_class = AssinarDocumentoForm
    model = Documento
    slug_field = 'pk_uuid'
    success_url = reverse_lazy('documentos:list')
    group_pk_url_kwarg = 'group_id'
    group_object = None
    grupo_assinante_backend = None

    def get(self, request, *args, **kwargs):
        self.grupo_assinante_backend = get_grupo_assinante_backend()
        group_id = self.kwargs.get(self.group_pk_url_kwarg, None)
        if group_id:
            self.group_object = self.grupo_assinante_backend.get_grupo_model().objects.get(pk=group_id)
        ret = super(AssinarDocumentoView, self).get(request, *args, **kwargs)
        if self.group_object and self.grupo_assinante_backend.grupo_ja_assinou(self.document_object, self.request.user,
                                                                               grupo_assinante=self.group_object):
            return HttpResponseRedirect(
                reverse('documentos:assinaturas', kwargs={'slug': self.document_object.pk_uuid}))
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
        detail_url = reverse('documentos:validar-detail', kwargs={'slug': self.document_object.pk_uuid})
        return detail_url


class DocumentoDetailView(NextURLMixin, PopupMixin, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_detail.html'
    # template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'
    model = Documento
    slug_field = 'pk_uuid'

    def get_context_data(self, **kwargs):
        context = super(DocumentoDetailView, self).get_context_data(**kwargs)

        context['url_imprimir_pdf'] = reverse('documentos:validar_detail_pdf',
                                              kwargs={'slug': self.object.pk_uuid})
        return context


class DocumentoDetailValidarView(QRCodeValidacaoMixin, DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'

    def render_to_response(self, context, **response_kwargs):
        return super(DocumentoDetailValidarView, self).render_to_response(context, **response_kwargs)


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
