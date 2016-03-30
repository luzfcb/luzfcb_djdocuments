# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import status
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import redirect, resolve_url
from django.utils import six
from django.utils.translation import ugettext as _

from ..models import Documento

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


class SingleDocumentObjectMixin(object):
    """
    Provides the ability to retrieve a single Document object for further manipulation.
    """
    document_model = Documento
    document_queryset = None
    document_slug_field = 'slug'
    document_context_object_name = None
    document_slug_url_kwarg = 'slug'
    document_pk_url_kwarg = 'document_pk'
    document_query_pk_and_slug = False

    def get_document_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_document_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.document_pk_url_kwarg, None)
        slug = self.kwargs.get(self.document_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.document_query_pk_and_slug):
            slug_field = self.get_document_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_document_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.

        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overridden.
        """
        if self.document_queryset is None:
            if self.document_model:
                return self.document_model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.document_queryset.all()

    def get_document_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.document_slug_field

    def get_document_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.document_context_object_name:
            return self.document_context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None






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
