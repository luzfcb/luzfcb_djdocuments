# -*- coding: utf-8 -*-
import status
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, resolve_url
from django.utils import six


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


class AjaxFormPostMixin(object):
    document_json_fields = ('pk', 'versao_numero')

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
