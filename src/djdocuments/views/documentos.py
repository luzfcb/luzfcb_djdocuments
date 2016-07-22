# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import ManyToManyField
from django.db.utils import IntegrityError
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from luzfcb_dj_simplelock.views import LuzfcbLockMixin

from djdocuments.utils import get_grupo_assinante_backend
from ..forms import AssinarDocumentoForm, CriarDocumentoForm, CriarModeloDocumentoForm, DocumentoEditarForm, \
    AdicionarAssinantesForm
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
    VinculateMixin
)

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


class DocumentoListView(LoginRequiredMixin, generic.ListView):
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


class DocumentoCriar(LoginRequiredMixin, VinculateMixin, generic.FormView):
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


class VincularDocumentoBaseView(LoginRequiredMixin, SingleDocumentObjectMixin, SingleObjectMixin, generic.View):
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


class DocumentoAssinaturasListView(LoginRequiredMixin, SingleDocumentObjectMixin, generic.ListView):
    model = Assinatura
    document_slug_field = 'pk_uuid'
    template_name = 'luzfcb_djdocuments/assinaturas_pendentes.html'

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
        return context


class AdicionarAssinantes(LoginRequiredMixin, SingleDocumentObjectMixin, generic.FormView):
    form_class = AdicionarAssinantesForm
    template_name = 'luzfcb_djdocuments/assinar_adicionar_assinantes.html'
    success_url = reverse_lazy('documentos:list')

    def get_form_kwargs(self):
        kwargs = super(AdicionarAssinantes, self).get_form_kwargs()
        grupos_ja_adicionados = self.document_object.grupos_assinates.all()
        kwargs.update({'grupos_ja_adicionados': grupos_ja_adicionados})
        return kwargs

    def form_valid(self, form):
        ret = super(AdicionarAssinantes, self).form_valid(form)

        grupo_para_adicionar = form.cleaned_data.get('grupo_para_adicionar')
        self.document_object.adicionar_grupos_assinantes(grupo_para_adicionar, self.request.user)
        return ret


class AssinarDocumentoView(LoginRequiredMixin, DocumentoAssinadoRedirectMixin, SingleDocumentObjectMixin,
                           generic.FormView):
    template_name = 'luzfcb_djdocuments/documento_assinar.html'
    # form_class = AssinarDocumentoForm
    model = Documento
    slug_field = 'pk_uuid'
    success_url = reverse_lazy('documentos:list')
    group_pk_url_kwarg = 'group_id'

    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        return super(AssinarDocumentoView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        from django import forms
        from django.contrib.auth.hashers import check_password
        from django.utils.translation import ugettext_lazy as _
        from dal import autocomplete
        from ..forms import (BootstrapFormInputMixin, UserModelChoiceField, UserModelMultipleChoiceField,
                             GrupoModelChoiceField)
        from ..widgets import ModelSelect2ForwardExtras
        group_id = self.kwargs.get(self.group_pk_url_kwarg, None)

        url_autocomplete = reverse('documentos:grupos-assinantes-do-documento', kwargs={'slug': self.document_object.pk_uuid})

        class AssinarDocumentoForm(BootstrapFormInputMixin, forms.Form):
            # titulo = forms.CharField(max_length=500)]
            grupo = forms.ChoiceField(
                label=get_grupo_assinante_backend().get_group_label(),
                help_text="Selecione o {}".format(get_grupo_assinante_backend().get_group_label()),
                # queryset=get_grupo_assinante_model_class().objects.all(),
                widget=autocomplete.ModelSelect2(url=url_autocomplete, forward=('grupo',)),
            )

            assinado_por = UserModelChoiceField(
                label="Assinante",
                help_text="Selecione o usuário que irá assinar o documento",
                # queryset=get_real_user_model_class().objects.all().order_by('username'),
                queryset=get_real_user_model_class().objects.all().order_by('username'),
                widget=ModelSelect2ForwardExtras(url='documentos:user-by-group-autocomplete',
                                                 forward=('grupo',), clear_on_change=('grupo',)),

            )

            password = forms.CharField(label="Senha",
                                       help_text="Digite a senha do usuário selecionado",
                                       widget=forms.PasswordInput())

            incluir_assinantes = UserModelMultipleChoiceField(
                required=False,
                label="Incluir assinantes e notificar",
                help_text="Incluir assinantes e notificar",
                queryset=get_real_user_model_class().objects.all().order_by('username'),
                widget=autocomplete.ModelSelect2Multiple(url='documentos:user-autocomplete',
                                                         forward=('assinado_por',),
                                                         ),

            )

            error_messages = {
                'invalid_login': _("Please enter a correct %(username)s and password. "
                                   "Note that both fields may be case-sensitive."),
                'inactive': _("This account is inactive."),
            }

            def __init__(self, *args, **kwargs):
                self.current_logged_user = kwargs.pop('current_logged_user')
                grupo_escolhido_queryset = kwargs.get('grupo_escolhido_queryset')
                grupo_escolhido = kwargs.get('grupo_escolhido')
                if grupo_escolhido_queryset:
                    kwargs.pop('grupo_escolhido_queryset')
                    kwargs.pop('grupo_escolhido')
                self.grupo_escolhido = grupo_escolhido
                super(AssinarDocumentoForm, self).__init__(*args, **kwargs)

                if grupo_escolhido_queryset:
                    self.initial['assinado_por'] = self.current_logged_user
                    backend = get_grupo_assinante_backend()
                    # grupo_escolhido_queryset = get_grupo_assinante_backend().get_grupo(pk=grupo_escolhido_pk,
                    #                                                                    use_filter=True)
                    # grupo_escolhido_queryset = backend.get_grupo(pk=grupo_escolhido_pk,
                    #                                              use_filter=True)
                    if not grupo_escolhido_queryset:
                        pass
                        # raise backend.get_grupo_model.
                    self.fields['grupo'] = GrupoModelChoiceField(
                        label=get_grupo_assinante_backend().get_group_label(),
                        help_text="Selecione o {}".format(get_grupo_assinante_backend().get_group_label()),
                        queryset=grupo_escolhido_queryset,
                        required=False,
                        empty_label=None,
                        initial=self.grupo_escolhido,
                        widget=forms.Select(attrs={'class': 'form-control', 'readonly': True, 'disabled': 'disabled'})
                    )
                    self.fields['assinado_por'].queryset = get_grupo_assinante_backend().get_usuarios_grupo(
                        self.grupo_escolhido)

            def clean_grupo(self):
                if self.grupo_escolhido:
                    return self.grupo_escolhido
                return self.cleaned_data['grupo']

            class Meta:
                model = Documento
                # fields = '__all__'
                fields = ('grupo', 'assinado_por', 'password')

            def clean_assinado_por(self):
                assinado_por = self.cleaned_data.get('assinado_por')
                print('AssinarDocumentoForm: pk', assinado_por.pk, 'username', assinado_por.get_full_name())
                return assinado_por

            def clean_password(self):
                password = self.cleaned_data.get('password')
                user = self.cleaned_data.get('assinado_por')
                valid = check_password(password, user.password)
                if not valid:
                    raise forms.ValidationError('Invalid password')

                return password

            def save(self, commit=True):
                documento = super(AssinarDocumentoForm, self).save(False)
                return documento

        return AssinarDocumentoForm

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

        return context

    def form_valid(self, form):
        ret = super(AssinarDocumentoView, self).form_valid(form)
        grupo_selecionado = form.cleaned_data['grupo']
        assinado_por = form.cleaned_data['assinado_por']
        senha = form.cleaned_data['password']
        backend = get_grupo_assinante_backend()
        self.document_object.assinar(grupo_assinante=grupo_selecionado, usuario_assinante=assinado_por, senha=senha)
        return ret

    def get_success_url(self):
        detail_url = reverse('documentos:validar-detail', kwargs={'pk': self.object.pk_uuid})
        return detail_url
