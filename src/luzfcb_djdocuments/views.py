# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json

import status
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, resolve_url
from django.utils import six
from django.views import generic
from dal import autocomplete
from luzfcb_dj_simplelock.views import LuzfcbLockMixin

from .utils.module_loading import get_real_user_model_class
# from phantom_pdf import render_to_pdf
from simple_history.views import HistoryRecordListViewMixin, RevertFromHistoryRecordViewMixin
from braces.views import LoginRequiredMixin
from .forms import (
    AssinarDocumento, DocumentoFormCreate, DocumentoFormUpdate2, DocumentoRevertForm, DocumetoValidarForm,
)
from .models import Documento
from .utils import add_querystrings_to_url
# from .models import DocumentoConteudo

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_MODEL = get_real_user_model_class()


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return USER_MODEL.objects.none()

        qs = USER_MODEL.objects.all()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

            # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
            # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        return result.get_full_name().title()


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            print('eh ajax')
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


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


class NextURLMixin(object):
    next_kwarg_name = 'next'
    next_page_url = None

    def get_next_kwarg_name(self):
        if not hasattr(self, 'next_kwarg_name'):
            raise ImproperlyConfigured(
                '{0} is missing an next_kwarg_name.'
                ' Define '
                '{0}.next_kwarg_name or override '
                '{0}.get_next_kwarg_name().'.format(
                    self.__class__.__name__))
        return self.next_kwarg_name

    def get_next_page_url(self):
        next_kwarg_name = self.get_next_kwarg_name()
        next_page = None

        if not hasattr(self, 'next_page_url'):
            raise ImproperlyConfigured(
                '{0} is missing an next_page_url '
                'url to redirect to. Define '
                '{0}.next_page_url or override '
                '{0}.get_next_page_url().'.format(
                    self.__class__.__name__))

        if self.next_page_url is not None:
            # print('if self.next_page_url is not None:')
            next_page = resolve_url(self.next_page_url)

        if next_kwarg_name in self.request.POST or next_kwarg_name in self.request.GET:
            # print('if next_kwarg_name in self.request.POST or next_kwarg_name in self.request.GET: id:', id(self))
            next_page = self.request.POST.get(next_kwarg_name,
                                              self.request.GET.get(next_kwarg_name))
            # Security check -- don't allow redirection to a different host.
            # if not is_safe_url(url=next_page, host=self.request.get_host()):
            #     next_page = self.request.path

        return next_page

    def form_valid(self, form):
        self.next_page_url = form.cleaned_data.get('proximo')
        return super(NextURLMixin, self).form_valid(form)

    def get_initial(self):
        initial = super(NextURLMixin, self).get_initial()
        initial.update({'proximo': self.get_next_page_url()})
        return initial

    def post(self, request, *args, **kwargs):
        ret = super(NextURLMixin, self).post(request, *args, **kwargs)
        self.next_page_url = self.get_next_page_url()
        return ret

    #
    def get(self, *args, **kwargs):
        ret = super(NextURLMixin, self).get(*args, **kwargs)
        self.next_page_url = self.get_next_page_url()
        return ret

    def get_context_data(self, **kwargs):

        context = super(NextURLMixin, self).get_context_data(**kwargs)
        next_kwarg_name = self.next_kwarg_name  # self.get_next_kwarg_name()
        next_page_url = self.next_page_url or self.get_next_page_url()
        context['next_kwarg_name'] = next_kwarg_name
        context['next_page_url'] = next_page_url
        if next_kwarg_name and next_page_url:
            context['next_page_paran'] = '{}={}'.format(next_kwarg_name, next_page_url)
        else:
            context['next_page_paran'] = ''
        # context['next_url2'] = self.request.build_absolute_uri(self.get_next_page_url())
        return context


class DocumentoListView(generic.ListView):
    template_name = 'luzfcb_djdocuments/documento_list.html'
    model = Documento

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


class AuditavelViewMixin(object):
    def form_valid(self, form):
        if hasattr(self.request, 'user') and not isinstance(self.request.user, AnonymousUser):
            if not form.instance.criado_por:
                form.instance.criado_por = self.request.user
            form.instance.modificado_por = self.request.user
        return super(AuditavelViewMixin, self).form_valid(form)


class PopupMixin(object):
    def get_initial(self):
        initial = super(PopupMixin, self).get_initial()
        initial.update({'is_popup': self.get_is_popup()})
        return initial

    def get_is_popup(self):
        if self.request.GET.get('popup', False):
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(PopupMixin, self).get_context_data(**kwargs)
        is_popup = self.get_is_popup()
        context['popup'] = is_popup
        if is_popup:
            context['popup_paran'] = 'popup=1'
        else:
            context['popup_paran'] = ''
        return context


class CopyDocumentContentMixin(object):
    def get_initial(self):
        initial = super(CopyDocumentContentMixin, self).get_initial()
        documento_instance = self.get_documento_instance()
        if documento_instance:
            initial.update({
                'conteudo': documento_instance.conteudo}
            )
        return initial

    def get_documento_pk(self):
        documento_pk = self.request.GET.get('djddoc', False)
        if documento_pk:
            if isinstance(documento_pk, six.string_types):
                documento_pk = int(documento_pk)
            if documento_pk <= 0:
                return False
        return documento_pk

    def get_documento_instance(self):
        documento_pk = self.get_documento_pk()
        if documento_pk:
            return self.model.objects.get(id=documento_pk)
        return documento_pk


class DocumentoCreateView(AjaxableResponseMixin, CopyDocumentContentMixin, NextURLMixin, PopupMixin, AuditavelViewMixin,
                          generic.CreateView):
    template_name = 'luzfcb_djdocuments/documento_create.html'
    model = Documento
    form_class = DocumentoFormCreate
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


class DocumentoAssinadoRedirectMixin(object):
    def get(self, request, *args, **kwargs):
        ret = super(DocumentoAssinadoRedirectMixin, self).get(request, *args, **kwargs)
        if self.object and self.object.esta_ativo:
            if self.object.esta_assinado:
                detail_url = reverse('documentos:detail', kwargs={'pk': self.object.pk})
                messages.add_message(request, messages.INFO,
                                     'Documentos assinados só podem ser visualizados - {}'.format(
                                         self.__class__.__name__))
                return redirect(detail_url, permanent=False)
        return ret


class DocumentoUpdateView(DocumentoAssinadoRedirectMixin,
                          AuditavelViewMixin,
                          # NextURLMixin,
                          PopupMixin,
                          generic.UpdateView):
    template_name = 'luzfcb_djdocuments/documento_update_2_ck_manual.html'
    # template_name = 'luzfcb_djdocuments/documento_update.html'
    model = Documento
    # form_class = DocumentoFormCreate
    form_class = DocumentoFormUpdate2
    # success_url = reverse_lazy('documentos:list')
    success_url = None

    # def get_success_url(self):
    #     next_kwarg_name = self.get_next_kwarg_name()
    #     next_page_url = self.get_next_page_url()
    #     is_popup = self.get_is_popup()
    #
    #     document_param_name = 'document'
    #     document_param_value = self.object.pk
    #
    #     doc = {
    #         document_param_name: document_param_value
    #     }
    #
    #     next_url = add_querystrings_to_url(next_page_url, doc)
    #     if not is_popup and next_page_url:
    #         # print('aqui')
    #         return next_url
    #
    #     if not next_page_url:
    #         return reverse('documentos:detail', {'pk': self.object.pk})
    #
    #     close_url = add_querystrings_to_url(reverse('documentos:close'), {next_kwarg_name: next_url})
    #
    #     return close_url
    # def get_success_url(self):
    #     next_kwarg_name = self.get_next_kwarg_name()
    #     next_page_url = self.get_next_page_url()
    #     is_popup = self.get_is_popup()
    #     new_url = add_querystrings_to_url(reverse('documentos:update', kwargs={'pk': self.object.pk}), {next_kwarg_name: next_page_url})
    #     if is_popup:
    #         new_url = add_querystrings_to_url(new_url, {'popup': 1})
    #     return new_url

    def form_invalid(self, form):
        response = super(DocumentoUpdateView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(DocumentoUpdateView, self).form_valid(form)
        if self.request.is_ajax():
            print('eh ajax')
            data = {
                'pk': self.object.pk,
                'conteudo': self.object.conteudo
            }
            return JsonResponse(data)
        else:
            return response


class DocumentoHistoryView(HistoryRecordListViewMixin, NextURLMixin, PopupMixin, generic.DetailView):
    template_name = 'luzfcb_djdocuments/documento_detail_with_versions.html'
    model = Documento
    history_records_paginate_by = 2


class DocumentoRevertView(RevertFromHistoryRecordViewMixin, NextURLMixin, AuditavelViewMixin, generic.UpdateView):
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


class DocumentoDetailValidarView(DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_validacao_detail.html'


class PDFViewer(generic.TemplateView):
    template_name = 'luzfcb_djdocuments/pdf_viewer.html'


class AssinarDocumentoView(DocumentoAssinadoRedirectMixin, AuditavelViewMixin, generic.UpdateView):
    template_name = 'luzfcb_djdocuments/documento_assinar_apagar.html'
    form_class = AssinarDocumento
    model = Documento

    success_url = reverse_lazy('documentos:list')

    def get_initial(self):
        initial = super(AssinarDocumentoView, self).get_initial()
        # copia o dicionario, para evitar mudar acidentalmente um dicionario mutavel
        initial = initial.copy()
        USER_MODEL.objects.get(id=2)
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


class AssinarDocumentoView2(generic.UpdateView):
    template_name = 'luzfcb_djdocuments/documento_assinar.html'
    form_class = AssinarDocumento
    model = Documento
    # fields = ('conteudo', )

    success_url = reverse_lazy('documentos:list')

    def get_form_kwargs(self):
        kwargs = super(AssinarDocumentoView2, self).get_form_kwargs()
        current_logged_user = self.request.user
        kwargs['current_logged_user'] = current_logged_user
        return kwargs


class ImprimirView(DocumentoDetailView):
    template_name = 'luzfcb_djdocuments/documento_print.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """

        if self.request.GET.get('pdf'):

            # return render_to_pdf(self.request, 'saida', format='A4', orientation='portrait')
            print('teste')
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs
            )


class AjaxFormPostMixin(object):
    document_json_fields = ('pk',)

    def form_valid(self, form):
        response = super(AjaxFormPostMixin, self).form_valid(form)
        if self.request.is_ajax():
            obj = self.get_object()
            data = {}
            for field in self.document_json_fields:
                data[field] = getattr(obj, field)
            data['errors'] = form.errors
            data['success_url'] = self.get_success_url()
            return JsonResponse(data=data)
        return response

    def form_invalid(self, form):
        response = super(AjaxFormPostMixin, self).form_invalid(form)
        if self.request.is_ajax():
            obj = self.get_object()
            data = {}
            for field in self.document_json_fields:
                data[field] = getattr(obj, field)
            data['errors'] = form.errors
            data['success_url'] = self.get_success_url()
            return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
        return response


class AjaxUpdateTesteApagar(LoginRequiredMixin,
                            AjaxFormPostMixin,
                            DocumentoAssinadoRedirectMixin,
                            AuditavelViewMixin,
                            NextURLMixin,
                            PopupMixin,
                            LuzfcbLockMixin,
                            generic.UpdateView):
    detail_view_named_url = 'documentos:detail'
    document_json_fields = ('titulo', 'document_number', 'document_version_number', 'identificador_versao')
    template_name = 'luzfcb_djdocuments/documento_update_2_ck_manual2.html'
    # template_name = 'luzfcb_djdocuments/documento_update.html'
    lock_revalidated_at_every_x_seconds = 1
    model = Documento
    prefix = 'document'
    # form_class = DocumentoFormCreate
    form_class = DocumentoFormUpdate2
    success_url = reverse_lazy('documentos:list')

    def get_lock_url_to_redirect_if_locked(self):
        return reverse('documentos:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        return super(AjaxUpdateTesteApagar, self).form_valid(form)

        # success_url = None

    def get(self, request, *args, **kwargs):
        return super(AjaxUpdateTesteApagar, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(AjaxUpdateTesteApagar, self).post(request, *args, **kwargs)
