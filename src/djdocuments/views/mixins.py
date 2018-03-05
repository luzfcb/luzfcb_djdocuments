# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import pyqrcode
import status
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import redirect, resolve_url
from django.utils import six
from django.utils.translation import ugettext as _

from djdocuments.utils.http import is_safe_url

from ..models import Documento
from ..utils.base64utils import png_as_base64_str, gerar_tag_img_base64_png_qr_str

USER_MODEL = get_user_model()


class FormActionViewMixin(object):
    form_action = None

    def get_form_action(self):
        if not self.form_action:
            raise ImproperlyConfigured(
                "%(cls)s is missing a 'form_action'. Define "
                "%(cls)s.form_action, or override "
                "%(cls)s.get_form_action()." % {
                    'cls': self.__class__.__name__
                }
            )
        return self.form_action

    def get_context_data(self, **kwargs):
        context = super(FormActionViewMixin, self).get_context_data(**kwargs)
        context['form_action'] = self.get_form_action()
        return context


class QRCodeValidacaoMixin(object):

    def get_context_data(self, **kwargs):
        # http://stackoverflow.com/a/7389616/2975300
        context = super(QRCodeValidacaoMixin, self).get_context_data(**kwargs)

        img_tag = gerar_tag_img_base64_png_qr_str(self.request, self.object)
        #
        context.update(
            {
                'qr_code_validation_html_img_tag': img_tag
            }
        )

        return context


#
# class NextURLMixin(object):
#     next_kwarg_name = 'next'
#     next_page_url = None
#
#     def get_next_kwarg_name(self):
#         if not hasattr(self, 'next_kwarg_name'):
#             raise ImproperlyConfigured(
#                 '{0} is missing an next_kwarg_name.'
#                 ' Define '
#                 '{0}.next_kwarg_name or override '
#                 '{0}.get_next_kwarg_name().'.format(
#                     self.__class__.__name__))
#         return self.next_kwarg_name
#
#     def get_next_page_url(self):
#         next_kwarg_name = self.get_next_kwarg_name()
#         next_page_url = None
#
#         if not hasattr(self, 'next_page_url'):
#             raise ImproperlyConfigured(
#                 '{0} is missing an next_page_url '
#                 'url to redirect to. Define '
#                 '{0}.next_page_url or override '
#                 '{0}.get_next_page_url().'.format(
#                     self.__class__.__name__))
#
#         if self.next_page_url is not None:
#             # print('if self.next_page_url is not None:')
#             next_page_url = resolve_url(self.next_page_url)
#
#         if next_kwarg_name in self.request.POST or next_kwarg_name in self.request.GET:
#             # print('if next_kwarg_name in self.request.POST or next_kwarg_name in self.request.GET: id:', id(self))
#             next_page_url = self.request.POST.get(next_kwarg_name,
#                                               self.request.GET.get(next_kwarg_name))
#             # Security check -- don't allow redirection to a different host.
#             # if not is_safe_url(url=next_page_url, host=self.request.get_host()):
#             #     next_page_url = self.request.path
#
#         return next_page_url
#
#     def form_valid(self, form):
#         self.next_page_url = form.cleaned_data.get('proximo')
#         return super(NextURLMixin, self).form_valid(form)
#
#     def get_initial(self):
#         initial = super(NextURLMixin, self).get_initial()
#         initial.update({'proximo': self.get_next_page_url()})
#         return initial
#
#     def post(self, request, *args, **kwargs):
#         ret = super(NextURLMixin, self).post(request, *args, **kwargs)
#         self.next_page_url = self.get_next_page_url()
#         return ret
#
#     #
#     def get(self, *args, **kwargs):
#         ret = super(NextURLMixin, self).get(*args, **kwargs)
#         self.next_page_url = self.get_next_page_url()
#         return ret
#
#     def get_context_data(self, **kwargs):
#
#         context = super(NextURLMixin, self).get_context_data(**kwargs)
#         next_kwarg_name = self.next_kwarg_name  # self.get_next_kwarg_name()
#         next_page_url = self.next_page_url or self.get_next_page_url()
#         context['next_kwarg_name'] = next_kwarg_name
#         context['next_page_url'] = next_page_url
#         if next_kwarg_name and next_page_url:
#             context['next_page_paran'] = '{}={}'.format(next_kwarg_name, next_page_url)
#         else:
#             context['next_page_paran'] = ''
#         # context['next_url2'] = self.request.build_absolute_uri(self.get_next_page_url())
#         return context


class SingleDocumentObjectMixin(object):
    """
    Provides the ability to retrieve a single Document object for further manipulation.
    """
    document_object = None
    document_model = Documento
    document_queryset = None
    document_slug_field = 'pk_uuid'
    document_context_object_name = 'document_object'
    document_slug_url_kwarg = 'slug'
    document_pk_url_kwarg = 'document_pk'
    document_query_pk_and_slug = False
    document_disable_if_url_kwarg_not_is_available = False

    def get(self, request, *args, **kwargs):
        if not self.document_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.document_pk_url_kwarg, None) or self.kwargs.get(self.document_slug_url_kwarg,
                                                                                     None)):
            self.document_object = self.get_document_object()
        return super(SingleDocumentObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.document_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.document_pk_url_kwarg, None) or self.kwargs.get(self.document_slug_url_kwarg,
                                                                                     None)):
            self.document_object = self.get_document_object()
        return super(SingleDocumentObjectMixin, self).post(request, *args, **kwargs)

    def get_document_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.document_queryset` and a `pk` or `slug` argument
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
        `get_document_object` and may not be called if `get_document_object` is overridden.
        """
        if self.document_queryset is None:
            if self.document_model:
                return self.document_model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.document_model, %(cls)s.document_queryset, or override "
                    "%(cls)s.get_document_queryset()." % {
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

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = super(SingleDocumentObjectMixin, self).get_context_data(**kwargs)
        if self.document_object:
            context['document_object'] = self.document_object
            context_object_name = self.get_document_context_object_name(self.document_object)
            if context_object_name:
                context[context_object_name] = self.document_object
        context.update(kwargs)
        return context


class SingleGroupObjectMixin(object):
    """
    Provides the ability to retrieve a single 'Group' object for further manipulation.
    """
    group_object = None
    group_model = None
    group_queryset = None
    group_slug_field = 'slug'
    group_context_object_name = 'group_object'
    group_slug_url_kwarg = 'group_slug'
    group_pk_url_kwarg = 'group_pk'
    group_query_pk_and_slug = False
    group_disable_if_url_kwarg_not_is_available = False

    def __init__(self):
        from ..utils import get_grupo_assinante_model_class
        self.group_model = get_grupo_assinante_model_class()
        super(SingleGroupObjectMixin, self).__init__()

    def get(self, request, *args, **kwargs):
        if not self.group_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.group_pk_url_kwarg, None) or self.kwargs.get(self.group_slug_url_kwarg, None)):
            self.group_object = self.get_group_object()
        return super(SingleGroupObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.group_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.group_pk_url_kwarg, None) or self.kwargs.get(self.group_slug_url_kwarg, None)):
            self.group_object = self.get_group_object()
        return super(SingleGroupObjectMixin, self).post(request, *args, **kwargs)

    def get_group_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.group_queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_group_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.group_pk_url_kwarg, None)
        slug = self.kwargs.get(self.group_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.group_query_pk_and_slug):
            slug_field = self.get_group_slug_field()
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

    def get_group_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.

        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overridden.
        """
        if self.group_queryset is None:
            if self.group_model:
                return self.group_model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.group_model, %(cls)s.group_queryset, or override "
                    "%(cls)s.get_group_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.group_queryset.all()

    def get_group_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.group_slug_field

    def get_group_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.group_context_object_name:
            return self.group_context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = super(SingleGroupObjectMixin, self).get_context_data(**kwargs)
        if self.group_object:
            context['group_object'] = self.group_object
            context_object_name = self.get_group_context_object_name(self.group_object)
            if context_object_name:
                context[context_object_name] = self.group_object
        context.update(kwargs)
        return context


class SingleUserObjectMixin(object):
    """
    Provides the ability to retrieve a single 'User' object for further manipulation.
    """
    user_object = None
    user_model = None
    user_queryset = None
    user_slug_field = 'username'
    user_context_object_name = 'user_object'
    user_slug_url_kwarg = 'user_slug'
    user_pk_url_kwarg = 'user_pk'
    user_query_pk_and_slug = False
    user_disable_if_url_kwarg_not_is_available = False

    def __init__(self):
        self.user_model = USER_MODEL
        super(SingleUserObjectMixin, self).__init__()

    def get(self, request, *args, **kwargs):
        if not self.user_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.user_pk_url_kwarg, None) or self.kwargs.get(self.user_slug_url_kwarg, None)):
            self.user_object = self.get_user_object()
        return super(SingleUserObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.user_disable_if_url_kwarg_not_is_available or (
                self.kwargs.get(self.user_pk_url_kwarg, None) or self.kwargs.get(self.user_slug_url_kwarg, None)):
            self.user_object = self.get_user_object()
        return super(SingleUserObjectMixin, self).post(request, *args, **kwargs)

    def get_user_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.user_queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_user_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.user_pk_url_kwarg, None)
        slug = self.kwargs.get(self.user_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.user_query_pk_and_slug):
            slug_field = self.get_user_slug_field()
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

    def get_user_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.

        Note that this method is called by the default implementation of
        `get_user_object` and may not be called if `get_user_object` is overridden.
        """
        if self.user_queryset is None:
            if self.user_model:
                return self.user_model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.user_model, %(cls)s.user_queryset, or override "
                    "%(cls)s.get_user_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.user_queryset.all()

    def get_user_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.user_slug_field

    def get_user_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.user_context_object_name:
            return self.user_context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = super(SingleUserObjectMixin, self).get_context_data(**kwargs)
        if self.user_object:
            context['user_object'] = self.user_object
            context_object_name = self.get_user_context_object_name(self.user_object)
            if context_object_name:
                context[context_object_name] = self.user_object
        context.update(kwargs)
        return context


class AuditavelViewMixin(object):
    def form_valid(self, form):
        if hasattr(self.request, 'user') and not isinstance(self.request.user, AnonymousUser):
            if not form.instance.criado_por:
                form.instance.criado_por = self.request.user
            form.instance.modificado_por = self.request.user
        return super(AuditavelViewMixin, self).form_valid(form)


class DjDocumentPopupMixin(object):
    def get_initial(self):
        initial = super(DjDocumentPopupMixin, self).get_initial()
        initial.update({'is_popup': self.get_is_popup()})
        return initial

    def get_is_popup(self):
        if self.request.GET.get('popup', False):
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(DjDocumentPopupMixin, self).get_context_data(**kwargs)
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

        # if self.object.esta_assinado_e_finalizado:
        #     detail_url = reverse('documentos:validar-detail', kwargs={'slug': self.object.pk_uuid})
        #     messages.add_message(request, messages.INFO,
        #                          'Documentos assinados só podem ser visualizados - {}')
        #     return redirect(detail_url, permanent=False)
        return ret


from django.views import generic


class AjaxFormPostMixin(object):
    document_json_fields = ('pk', 'versao_numero')
    template_name_ajax = None
    ajax_success_message = None

    def get_ajax_success_message(self, object_instance=None):
        return self.ajax_success_message

    def get_template_names(self):
        templates = super(AjaxFormPostMixin, self).get_template_names()
        if self.request.is_ajax() and self.template_name_ajax:
            templates = [self.template_name_ajax]
        return templates

    def get_form_fields(self):
        fields = self.document_json_fields
        if not fields:
            form = self.get_form()
            fields = six.iterkeys(form.fields)
        return fields

    def form_valid(self, form):
        response = super(AjaxFormPostMixin, self).form_valid(form)
        if self.request.is_ajax():
            object_instance = self.get_object_members()
            data = {'object_instance': object_instance, 'errors': form.errors,
                    'success_url': self.get_success_url()}
            message = self.get_ajax_success_message(object_instance)
            if message:
                messages.add_message(self.request, messages.SUCCESS, message)
            return JsonResponse(data=data)
        return response

    def get_object_members(self):
        data = {}
        if hasattr(self, 'object'):
            if not self.object:
                self.object = self.get_object()
            for field in self.get_form_fields():
                if hasattr(self.object, field):
                    field_instance = getattr(self.object, field)
                    if isinstance(field_instance, models.Model):
                        field_data = field_instance.pk
                    else:
                        field_data = field_instance
                    data[field] = field_data
        return data

    def form_invalid(self, form):
        response = super(AjaxFormPostMixin, self).form_invalid(form)
        if self.request.is_ajax():
            if hasattr(self, 'object') and not self.object:
                self.object = self.get_object()
            data = {}
            # members = self.get_object_members()
            data['errors'] = form.errors
            data['success_url'] = self.get_success_url()
            return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
        return response


class VinculateMixin(object):
    vinculate_view_field = 'v'
    vinculate_value_field = 'to'
    vinculate_view_name = None
    vinculate_value = None

    def get_vinculate_parameters(self):

        clean_vinculate_view_name = self.request.GET.get(self.vinculate_view_field, None)
        if isinstance(clean_vinculate_view_name, six.string_types):
            clean_vinculate_view_name = clean_vinculate_view_name.strip("'").strip('"')
        self.vinculate_view_name = clean_vinculate_view_name
        self.vinculate_value = self.request.GET.get(self.vinculate_value_field, None)
        if not self.vinculate_view_name and not self.vinculate_value:
            pass
        elif not self.vinculate_view_name or not self.vinculate_value:
            raise ImproperlyConfigured(
                "(cls)s has is missing %(vinculate_view_field)s or %(vinculate_value_field)s "
                "querystring on GET parameter"
                "provide %(vinculate_value_field)s=NAME_OF_VIEW and %(vinculate_value_field)s=PK_ " % {
                    'cls': self.__class__.__name__,
                    'vinculate_view_field': self.vinculate_view_field,
                    'vinculate_value_field': self.vinculate_value_field
                }
            )

    def get_context_data(self, **kwargs):
        context = super(VinculateMixin, self).get_context_data(**kwargs)
        self.get_vinculate_parameters()

        if self.vinculate_view_name and self.vinculate_value:
            context['vinculate_view_kwarg'] = '{}={}'.format(self.vinculate_view_field, self.vinculate_view_name)
            context['vinculate_value_kwarg'] = '{}={}'.format(self.vinculate_value_field, self.vinculate_value)
        return context


# backport of django 1.11
# https://github.com/django/django/blob/master/django/contrib/auth/views.py#L56-L62
class SuccessURLAllowedHostsMixin(object):
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        allowed_hosts = {self.request.get_host()}
        allowed_hosts.update(self.success_url_allowed_hosts)
        return allowed_hosts


class NextPageURLMixin(SuccessURLAllowedHostsMixin):
    next_page_url = None
    next_page_redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super(NextPageURLMixin, self).get_context_data(**kwargs)
        next_page_redirect_field_name = self.get_next_page_redirect_field_name()
        context['next_page_redirect_field_name'] = next_page_redirect_field_name
        context['next_page_url'] = self.get_next_page()
        return context

    def get_next_page_redirect_field_name(self):
        return self.next_page_redirect_field_name

    def get_next_page(self):
        next_page_redirect_field_name = self.get_next_page_redirect_field_name()
        if self.next_page_url is not None:
            next_page = resolve_url(self.next_page_url)
        else:
            http_referer = self.request.META.get('HTTP_REFERER')

            if http_referer:
                parsed = six.moves.urllib.parse.urlparse(http_referer)
                if not self.next_page_url:
                    next_page = parsed.path
            else:
                next_page = self.next_page_url

        if (next_page_redirect_field_name in self.request.POST or
                    next_page_redirect_field_name in self.request.GET):
            next_page = self.request.POST.get(
                next_page_redirect_field_name,
                self.request.GET.get(next_page_redirect_field_name)
            )
            url_is_safe = is_safe_url(
                url=next_page,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            # Security check -- Ensure the user-originating redirection URL is
            # safe.
            if not url_is_safe:
                next_page = self.request.path
        return next_page

    def get_success_url(self):
        next_page = self.get_next_page()
        if not self.get_next_page() == self.request.path:
            return next_page
        return super(NextPageURLMixin, self).get_success_url()


class MenuMixin(object):
    menu_atual = None

    def get_context_data(self, **kwargs):
        context = super(MenuMixin, self).get_context_data(**kwargs)
        context['menu_atual'] = self.menu_atual
        return context
