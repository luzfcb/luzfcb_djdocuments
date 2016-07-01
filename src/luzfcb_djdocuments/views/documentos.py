# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
# import the logging library
import logging

import pyqrcode
from braces.views import LoginRequiredMixin
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.defaultfilters import urlize
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from luzfcb_dj_simplelock.views import LuzfcbLockMixin
from urlobject import URLObject
from wkhtmltopdf.views import PDFRenderMixin

from luzfcb_djdocuments.views.mixins import (
    AjaxFormPostMixin,
    AuditavelViewMixin,
    CopyDocumentContentMixin,
    DocumentoAssinadoRedirectMixin,
    NextURLMixin,
    PopupMixin,
    SingleDocumentObjectMixin
)

from ..forms import (
    AssinarDocumentoForm,
    CriarDocumentoForm,
    CriarModeloDocumentoForm,
    DocumentoEditarForm,
    DocumentoRevertForm,
    DocumetoValidarForm
)
from ..models import Assinatura, Documento
from ..templatetags.luzfcb_djdocuments_tags import absolute_uri
from ..utils import add_querystrings_to_url
from ..utils.module_loading import get_real_user_model_class

# from phantom_pdf import render_to_pdf
# from simple_history.views import HistoryRecordListViewMixin, RevertFromHistoryRecordViewMixin


# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_MODEL = get_real_user_model_class()


# class AjaxableResponseMixin(object):
#     """
#     Mixin to add AJAX support to a form.
#     Must be used with an object-based FormView (e.g. CreateView)
#     """
#
#     def form_invalid(self, form):
#         response = super(AjaxableResponseMixin, self).form_invalid(form)
#         if self.request.is_ajax():
#             return JsonResponse(form.errors, status=400)
#         else:
#             return response
#
#     def form_valid(self, form):
#         # We make sure to call the parent's form_valid() method because
#         # it might do some processing (in the case of CreateView, it will
#         # call form.save() for example).
#         response = super(AjaxableResponseMixin, self).form_valid(form)
#         if self.request.is_ajax():
#             print('eh ajax')
#             data = {
#                 'pk': self.object.pk,
#             }
#             return JsonResponse(data)
#         else:
#             return response


class DocumentoGeneralDashboardView(generic.TemplateView):
    template_name = 'luzfcb_djdocuments/dashboard_general.html'


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


class DocumentoCreateView(CopyDocumentContentMixin,
                          NextURLMixin,
                          PopupMixin,
                          AuditavelViewMixin,
                          generic.CreateView):
    # template_name = 'luzfcb_djdocuments/documento_create2.html'
    model = Documento
    # form_class = DocumentoFormCreate
    form_class = DocumentoEditarForm
    success_url = reverse_lazy('documentos:list')
    is_popup = False

    # inlines = [DocumentoConteudoInline, ]

    def __init__(self, *args, **kwargs):
        super(DocumentoCreateView, self).__init__(*args, **kwargs)
        print('id: {}'.format(id(self)))

    def get_success_url(self):
        next_kwarg_name = self.get_next_kwarg_name()
        next_page_url = self.get_next_page_url()
        is_popup = self.get_is_popup()

        document_param_name = 'document'
        document_param_value = self.object.pk

        doc = {
            document_param_name: document_param_value
        }

        next_url = add_querystrings_to_url(next_page_url, doc)
        if not is_popup and next_page_url:
            # print('aqui')
            return next_url

        if not next_page_url:
            return reverse('documentos:detail', {'pk': self.object.pk})

        close_url = add_querystrings_to_url(reverse('documentos:close'), {next_kwarg_name: next_url})

        return close_url

    def get_initial(self):
        initial = super(DocumentoCreateView, self).get_initial()
        # initial.update({
        #                 'conteudo': BIG_SAMPLE_HTML}
        #                )
        if self.get_titulo():
            initial.update({
                'titulo': self.get_titulo()
            })
        from pprint import pprint
        pprint(initial)
        return initial

    def get_titulo(self):
        return self.request.GET.get('djdtitulo', False)

    def get(self, *args, **kwargs):
        original_response = super(DocumentoCreateView, self).get(*args, **kwargs)

        return original_response


class CloseView(NextURLMixin, generic.TemplateView):
    template_name = 'luzfcb_djdocuments/close_popup.html'

    def get_context_data(self, **kwargs):
        context = super(CloseView, self).get_context_data(**kwargs)
        context.update({
            'close': self.request.GET.get('close')
        }
        )

        return context


class DocumentoDetailView(NextURLMixin, PopupMixin, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_detail.html'
    # template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'
    model = Documento

    def get_context_data(self, **kwargs):
        context = super(DocumentoDetailView, self).get_context_data(**kwargs)
        conteudo = "{}{}{}".format(self.object.conteudo, self.object.versao_numero, self.request.user.username)
        signer = signing.Signer("{}-{}-{}".format(self.object.pk,
                                                  self.object.versao_numero, self.request.user.username))
        documento = signer.sign(conteudo)

        context.update(
            {
                'conteudo': conteudo,
                'conteudo_sign': documento
            }
        )
        return context


# class DocumentoHistoryView(HistoryRecordListViewMixin, NextURLMixin, PopupMixin, generic.DetailView):
class DocumentoHistoryView(NextURLMixin, PopupMixin, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_detail_with_versions.html'
    model = Documento
    history_records_paginate_by = 2


# class DocumentoRevertView(RevertFromHistoryRecordViewMixin, NextURLMixin, AuditavelViewMixin, generic.UpdateView):
class DocumentoRevertView(NextURLMixin, AuditavelViewMixin, generic.UpdateView):
    template_name = 'luzfcb_djdocuments/documento_revert.html'
    model = Documento
    form_class = DocumentoRevertForm

    # inlines = [DocumentoConteudoInline, ]

    def get_success_url(self):
        pk = self.get_object().pk
        sucess_url = reverse_lazy('documentos:detail', kwargs={'pk': pk})
        # print(sucess_url)
        return sucess_url

    def get_context_data(self, **kwargs):
        context = super(DocumentoRevertView, self).get_context_data(**kwargs)

        context.update({
            'object': self.object
        })
        return context

    def form_valid(self, form):
        if hasattr(self.request, 'user') and not isinstance(self.request.user, AnonymousUser):
            form.instance.revertido_por = self.request.user
            form.instance.revertido_da_versao = form.instance.versao_numero
        return super(DocumentoRevertView, self).form_valid(form)


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

            return HttpResponse(json.dumps(to_json_responce), content_type='application/json')
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
        pk = self.get_object().pk
        return reverse_lazy('documentos:validar-detail', kwargs={'pk': pk})

    def get_object(self):
        return self.documento_instance

    def form_valid(self, form):
        self.documento_instance = form.documento
        return super(DocumentoValidacaoView, self).form_valid(form)


def png_as_base64_str(qr_code, scale=3, module_color=(0, 0, 0, 255),
                      background=(255, 255, 255, 255), quiet_zone=4):
    import io
    import base64
    with io.BytesIO() as virtual_file:
        qr_code.png(file=virtual_file, scale=scale, module_color=module_color,
                    background=background, quiet_zone=quiet_zone)
        image_as_str = base64.b64encode(virtual_file.getvalue()).decode("ascii")
    return image_as_str


class TestePDF(PDFRenderMixin, generic.TemplateView):
    template_name = 'luzfcb_djdocuments/test_templates/base_pdf.html'

    pdf_template_name = 'luzfcb_djdocuments/test_templates/corpo.html'
    pdf_header_template = 'luzfcb_djdocuments/test_templates/cabecalho.html'
    pdf_footer_template = 'luzfcb_djdocuments/test_templates/rodape.html'

    show_content_in_browser = True
    cmd_options = {
        'print-media-type': True,

        # 'margin-top': '8.0mm',
        'margin-top': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '20cm',
        # 'page-width': '210mm',
        # 'page-height': '297mm',
        # 'viewport-size': '210mmX297mm',
        # 'orientation': 'Landscape',
        'page-size': 'A4'
    }


class AssinaturaPendenteView(LoginRequiredMixin, generic.ListView):
    model = Assinatura
    template_name = 'luzfcb_djdocuments/assinaturas_pendentes.html'

    def get_queryset(self):
        if hasattr(self.request, 'user') and not isinstance(self.request.user, AnonymousUser):
            aaaa = self.model.objects.select_related('documento', 'assinado_por').nao_assinados(self.request.user)
        else:
            aaaa = self.model.objects.select_related('documento', 'assinado_por').nao_assinados()
        return aaaa


class DocumentoDetailValidarView(PDFRenderMixin, DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'

    pdf_template_name = 'luzfcb_djdocuments/pdf/corpo.html'
    pdf_header_template = 'luzfcb_djdocuments/pdf/cabecalho.html'
    pdf_footer_template = 'luzfcb_djdocuments/pdf/rodape.html'

    show_content_in_browser = True
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

    def get_context_data(self, **kwargs):
        # http://stackoverflow.com/a/7389616/2975300
        context = super(DocumentoDetailValidarView, self).get_context_data(**kwargs)

        # possivel candidato para cache
        url_validar = reverse('documentos:validar')
        querystring = "{}={}".format('h', self.object.assinatura_hash_upper_limpo)
        url_com_querystring = URLObject(url_validar).with_query(querystring)
        url = absolute_uri(url_com_querystring, self.request)

        codigo_qr = pyqrcode.create(url)
        encoded_image = png_as_base64_str(qr_code=codigo_qr, scale=2)

        img_tag = "<img src=data:image/png;base64,{}>".format(encoded_image)
        #
        context.update(
            {
                'qr_code_validation_html_img_tag': img_tag
            }
        )

        return context

    def render_to_response(self, context, **response_kwargs):
        return super(DocumentoDetailValidarView, self).render_to_response(context, **response_kwargs)


class PDFViewer(generic.TemplateView):
    template_name = 'luzfcb_djdocuments/pdf_viewer.html'


class AssinarDocumentoView(DocumentoAssinadoRedirectMixin, generic.FormView, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_assinar.html'
    form_class = AssinarDocumentoForm
    model = Documento

    success_url = reverse_lazy('documentos:list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AssinarDocumentoView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AssinarDocumentoView, self).post(request, *args, **kwargs)

    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(AssinarDocumentoView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(AssinarDocumentoView, self).get_initial()
        # copia o dicionario, para evitar mudar acidentalmente um dicionario mutavel
        initial = initial.copy()
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated():
            initial.update({
                'assinado_por': user,
            }
            )
        return initial

    def get_form_kwargs(self):
        kwargs = super(AssinarDocumentoView, self).get_form_kwargs()
        current_logged_user = self.request.user
        kwargs['current_logged_user'] = current_logged_user
        return kwargs

    def form_valid(self, form):
        ret = super(AssinarDocumentoView, self).form_valid(form)
        ###################################
        # documento = form.save(False)
        documento = self.object

        assinado_por = form.cleaned_data.get('assinado_por')

        # cria ou obten instancia de Assinatura para o usuario selecionado em  assinado_por
        obj, created = Assinatura.objects.get_or_create(documento=documento,
                                                        assinado_por=assinado_por,
                                                        versao_numero=documento.versao_numero,
                                                        esta_ativo=True,
                                                        defaults={
                                                            'documento': documento,
                                                            'assinado_por': assinado_por,
                                                            'versao_numero': documento.versao_numero + 1,
                                                            'esta_ativo': True
                                                        }
                                                        )
        if created:
            print("criado : {}".format(obj.assinado_por.username))
        else:
            print("obtido")

        if not obj.esta_assinado:
            obj.assinar_documento()

        # cria assinatura
        usuarios_assinantes = form.cleaned_data.get('incluir_assinantes')
        for usuario_assinante in usuarios_assinantes:
            # Assinatura.objects.get
            obj, created = Assinatura.objects.get_or_create(documento=documento,
                                                            assinado_por=usuario_assinante,
                                                            versao_numero=documento.versao_numero,
                                                            defaults={
                                                                'documento': documento,
                                                                'assinado_por': usuario_assinante,
                                                                'versao_numero': documento.versao_numero + 1,
                                                                'esta_assinado': False
                                                            }
                                                            )
            if created:
                print("criado : {}".format(obj.assinado_por.username))
                # notificar usuario
            else:
                print("obtido")

        # documento.assinar_documento(
        #     assinado_por=form.cleaned_data.get('assinado_por'),
        #     current_logged_user=form.current_logged_user
        # )

        print(form.cleaned_data.get('incluir_assinantes'))
        # return documento
        ###################################
        assinado_por = form.cleaned_data.get('assinado_por', None)

        msg = 'Documento n°{} assinado com sucesso por {}'.format(
            self.object.identificador_versao,
            assinado_por.get_full_name().title()
        )
        messages.add_message(self.request, messages.INFO, msg)
        return ret

    def get_success_url(self):
        detail_url = reverse('documentos:validar-detail', kwargs={'pk': self.object.pk})
        return detail_url


class ImprimirView(DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_print_novo.html'

    def get(self, *args, **kwargs):
        original_response = super(ImprimirView, self).get(*args, **kwargs)
        if self.request.GET.get('pdf'):
            import pdfkit

            url = urlize(absolute_uri(self.request.resolver_match.url_name, request=self.request))
            return pdfkit.from_url(url, 'novo_arquivo.pdf')

        return original_response

    def get_context_data(self, **kwargs):
        context = super(ImprimirView, self).get_context_data(**kwargs)
        context.update({
            'disableTable': False
        })
        return context


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
    prefix = 'document'
    # form_class = DocumentoFormCreate
    form_class = DocumentoEditarForm
    success_url = reverse_lazy('documentos:list')

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).dispatch(request, *args, **kwargs)

    def get_lock_url_to_redirect_if_locked(self):
        return reverse('documentos:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        return super(DocumentoEditor, self).form_valid(form)

        # success_url = None

    def get(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DocumentoEditor, self).post(request, *args, **kwargs)


def create_from_template(current_user, documento_template):
    # template_documento = Documento.objects.get(pk=documento_template.pk)

    document_kwargs = {
        'cabecalho': documento_template.cabecalho,
        'titulo': documento_template.titulo,
        'conteudo': documento_template.conteudo,
        'rodape': documento_template.rodape,
        'tipo_documento': documento_template.tipo_documento,
        'criado_por': current_user,
        'modificado_por': current_user
    }

    documento_novo = Documento(**document_kwargs)
    documento_novo.save()

    return documento_novo


class DocumentoCriar(generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_create2.html'
    form_class = CriarDocumentoForm
    default_selected_document_template_pk = None
    vinculate_view_field = 'v'
    vinculate_value_field = 'to'
    vinculate_view_name = None
    vinculate_value = None
    document_pk_url_kwarg = 'document_pk'

    def form_valid(self, form):
        self.get_vinculate_parameters()
        modelo_documento = form.cleaned_data['modelo_documento']
        documento_novo = create_from_template(self.request.user, modelo_documento)
        # vinculate_view_name = self.request.GET.get(self.vinculate_view_field, None)
        # vinculate_value = self.request.GET.get(self.vinculate_value_field, None)

        if self.vinculate_view_name and self.vinculate_value:
            viculate_url = reverse(self.vinculate_view_name, kwargs={'document_pk': documento_novo.pk,
                                                                     'pk': self.vinculate_value})
            return redirect(viculate_url, permanent=True)
        else:
            editar_url = reverse('documentos:editar', kwargs={'pk': documento_novo.pk})
            return redirect(editar_url, permanent=True)

    def get_initial(self):
        initial = super(DocumentoCriar, self).get_initial()
        default_document_template = self.get_default_selected_document_template_pk()
        if default_document_template:
            initial.update({'modelo_documento': default_document_template})
        else:
            document_pk_modelo = self.request.GET.get(self.document_pk_url_kwarg)

            if document_pk_modelo:
                try:

                    documento_modelo = Documento.objects.get(pk=document_pk_modelo)
                except Documento.DoesNotExist:
                    pass
                else:
                    print(documento_modelo)
                    initial.update({
                        'tipo_documento': documento_modelo.tipo_documento,
                        'modelo_documento': documento_modelo.pk
                    })
        return initial

    def get_default_selected_document_template_pk(self):
        return self.default_selected_document_template_pk

    def get_vinculate_parameters(self):

        clean_vinculate_view_name = self.request.GET.get(self.vinculate_view_field, None)
        if isinstance(clean_vinculate_view_name, six.string_types):
            clean_vinculate_view_name = clean_vinculate_view_name.strip("'").strip('"')
        self.vinculate_view_name = clean_vinculate_view_name
        self.vinculate_value = self.request.GET.get(self.vinculate_value_field, None)

    def get_context_data(self, **kwargs):
        context = super(DocumentoCriar, self).get_context_data(**kwargs)
        self.get_vinculate_parameters()

        if self.vinculate_view_name and self.vinculate_value:
            context['vinculate_view_kwarg'] = '{}={}'.format(self.vinculate_view_field, self.vinculate_view_name)
            context['vinculate_value_kwarg'] = '{}={}'.format(self.vinculate_value_field, self.vinculate_value)
        return context


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


        editar_url = reverse(self.document_edit_named_view, kwargs={'pk': self.document_object.pk})
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
                    logger.info()
                    return True
        return False








        # kwargs_names = ['atendimento_numero', ]
        # kwargs_have_name = False
        # @never_cache
        # @login_required
        # def dispatch(self, request, *args, **kwargs):
        #     return super(VincularDocumentoTarefa, self).dispatch(request, *args, **kwargs)
        #
        #
        # def get(self, request, *args, **kwargs):
        #     ret = super(VincularDocumentoTarefa, self).get(request, *args, **kwargs)
        #
        #     tarefa = self.model.objects.get(id=self.kwargs.get('tarefa_id'))
        #     document = self.get_document_object()
        #     getattr()
        #
        #     if not tarefa.documentos.filter(id=document_id).count():
        #         try:
        #             tarefa.documentos.add(document_id)
        #         except IntegrityError as e:
        #             logger.error(e)
        #         else:
        #             tarefa.save()
        #
        #     d = {}
        #     for key in self.kwargs_names:
        #         d[key] = self.kwargs.get(key)
        #
        #     if self.kwargs_have_name:
        #         return redirect(self.to_view, **d)
        #     else:
        #         return redirect(self.to_view, *d.values())
