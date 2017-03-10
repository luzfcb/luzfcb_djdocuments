# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from captcha.fields import CaptchaField
from dal import autocomplete
from dj_waff.choice_with_other import ChoiceWithOtherField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_addanother.widgets import AddAnotherWidgetWrapper

from .backends import DjDocumentsBackendMixin
from .form_mixins import BootstrapFormInputMixin, ReadOnlyFieldsMixin
from .models import Assinatura, Documento, TipoDocumento
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
from .utils import get_djdocuments_backend, get_grupo_assinante_model_class
from .widgets import CkeditorTextAreadWidget, ModelSelect2ForwardExtras, SplitedHashField3

# TODO: remove this ugly hack
try:
    from test_project.test_app.tests import BIG_SAMPLE_HTML, CABECALHO, RODAPE, TITULO
except ImportError:
    BIG_SAMPLE_HTML = CABECALHO = RODAPE = TITULO = ' '

USER_MODEL = get_user_model()


class DocumentoEditarForm(forms.ModelForm):
    cabecalho = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        required=False,
        initial=CABECALHO,
    )
    # titulo = forms.CharField(
    #     widget=CkeditorTextAreadWidget,
    #     label='',
    #     initial=TITULO
    # )
    conteudo = forms.CharField(
        widget=CkeditorTextAreadWidget(attrs={'autofocus': True}),
        label='',
        required=False,
        initial=BIG_SAMPLE_HTML
    )
    rodape = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        required=False,
        initial=RODAPE
    )

    class Meta:
        model = Documento
        fields = (
            'cabecalho',
            # 'titulo',
            'conteudo',
            'rodape'
        )


class DocumentoEditarWithReadOnlyFieldsForm(ReadOnlyFieldsMixin, DocumentoEditarForm):
    readonly_fields = ('cabecalho', 'rodape')


class TipoDocumentoTemplateModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.titulo


class ModeloDocumentoTemplateModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        if obj.eh_modelo:
            ret = remover_tags_html(obj.modelo_descricao or 'Descricao modelo: {}'.format(obj.pk))
        else:
            ret = remover_tags_html(obj.identificador_versao)
        return ret


class GrupoModelChoiceField(DjDocumentsBackendMixin, forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return self.djdocuments_backend.get_grupo_name(obj)


class GrupoModelMultipleChoiceField(DjDocumentsBackendMixin, forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return self.djdocuments_backend.get_grupo_name(obj)


CRIAR_DOCUMENTO_CHOICES = [
    ('__padrao__', 'Nenhum'),
]


# BootstrapFormInputMixin
class CriarDocumentoForm(DjDocumentsBackendMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user')
        super(CriarDocumentoForm, self).__init__(*args, **kwargs)
        if self.current_user:
            self.fields['grupo'].queryset = self.djdocuments_backend.get_grupos_usuario(self.current_user)

    # titulo = forms.CharField(max_length=500)]
    grupo = GrupoModelChoiceField(
        label=get_djdocuments_backend().get_group_label(),
        queryset=get_grupo_assinante_model_class().objects.none()
    )

    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumento.objects.all(),
        widget=autocomplete.ModelSelect2(url='documentos:tipodocumento-autocomplete')
    )

    # modelo_documento = ChoiceWithOtherField(
    #     choices=CRIAR_DOCUMENTO_CHOICES,
    #     first_is_preselected=True,
    #     other_form_field=ModeloDocumentoTemplateModelChoiceField(
    #         label='Modelo de Documento',
    #         queryset=Documento.admin_objects.all(),
    #         widget=ModelSelect2ForwardExtras(url='documentos:documentocriar-autocomplete',
    #                                          forward=('tipo_documento',),
    #                                          clear_on_change=('tipo_documento',)
    #                                          ),
    #
    #     )
    # )
    modelo_documento = ChoiceWithOtherField(
        label='Modelo de Documento',
        choices=CRIAR_DOCUMENTO_CHOICES,
        first_is_preselected=True,
        other_form_field=ModeloDocumentoTemplateModelChoiceField(
            label='Modelo de Documento',
            to_field_name='pk_uuid',
            queryset=Documento.admin_objects.all(),
            widget=ModelSelect2ForwardExtras(url='documentos:documentocriar-autocomplete',
                                             to_field_name='pk_uuid',
                                             forward=('tipo_documento',),
                                             clear_on_change=('tipo_documento',),
                                             attrs={'data-preview': True},
                                             ),

        )
    )

    assunto = forms.CharField(
        label='Assunto do Documento',
        max_length=70,

    )

    # teste = DefaultOrModelChoiceField(choices=[('1', 'a'), ('2', 'b')])


class CriarDocumentoParaGrupoForm(CriarDocumentoForm):

    def __init__(self, *args, **kwargs):
        grupo_escolhido_queryset = kwargs.get('grupo_escolhido_queryset')
        self.grupo_escolhido = kwargs.get('grupo_escolhido')

        if grupo_escolhido_queryset:
            kwargs.pop('grupo_escolhido_queryset')
            kwargs.pop('grupo_escolhido')
        super(CriarDocumentoParaGrupoForm, self).__init__(*args, **kwargs)

        if self.grupo_escolhido:
            self.fields['grupo'] = GrupoModelChoiceField(
                label=self.djdocuments_backend.get_group_label(),
                help_text="Selecione o {}".format(self.djdocuments_backend.get_group_label()),
                queryset=grupo_escolhido_queryset,
                required=False,
                empty_label=None,
                initial=self.grupo_escolhido,
                widget=forms.Select(attrs={'class': 'form-control', 'readonly': True, 'disabled': 'disabled'})
            )

    def clean_grupo(self):
        if self.grupo_escolhido:
            return self.grupo_escolhido
        return self.cleaned_data['grupo']


# class CriarModeloDocumentoForm(BootstrapFormInputMixin, forms.Form):
# class CriarModeloDocumentoForm(CriarDocumentoForm):
#     # titulo = forms.CharField(max_length=500)
#     tipo_documento = TipoDocumentoTemplateModelChoiceField(
#         label='Tipo de Documento',
#         queryset=TipoDocumento.objects.all(),
#
#     )
#     modelo_documento = ModeloDocumentoTemplateModelChoiceField(
#         label='Modelo de Documento',
#         queryset=Documento.admin_objects.all(),
#         # widget=autocomplete.ModelSelect2(url='documentos:documentocriar-autocomplete',
#         #                                  forward=('tipo_documento',),
#         #                                  #clear_on_change=('tipo_documento',)
#         #                                  ),
#
#     )
#
#     modelo_descricao = forms.CharField(
#         label='Descrição do Modelo',
#         widget=forms.Textarea
#     )
class CriarModeloDocumentoForm(DjDocumentsBackendMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user')
        super(CriarModeloDocumentoForm, self).__init__(*args, **kwargs)
        if self.current_user:
            self.fields['grupo'].queryset = self.djdocuments_backend.get_grupos_usuario(self.current_user)

    # titulo = forms.CharField(max_length=500)]
    grupo = GrupoModelChoiceField(
        label=get_djdocuments_backend().get_group_label(),
        queryset=get_grupo_assinante_model_class().objects.none(),
        # required=False,
        widget=autocomplete.ModelSelect2(url='documentos:grupos_do_usuario_autocomplete'),

    )

    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumento.objects.all(),
        widget=AddAnotherWidgetWrapper(
            widget=autocomplete.ModelSelect2(url='documentos:tipodocumento-autocomplete', ),
            add_related_url=reverse_lazy('documentos:criar_tipo_documento'),
        )

    )

    modelo_descricao = forms.CharField(
        label='Descrição do Modelo',
        max_length=70,

    )


class CriarModeloDocumentoApartirDoDocumentoForm(CriarModeloDocumentoForm):

    def __init__(self, *args, **kwargs):
        self.document_object = kwargs.pop('document_object')
        # initial = {'modelo_documento': self.document_object.pk_uuid}
        super(CriarModeloDocumentoApartirDoDocumentoForm, self).__init__(*args, **kwargs)
        if self.document_object:
            self.fields['modelo_documento'].queryset = Documento.admin_objects.filter(
                pk_uuid=self.document_object.pk_uuid)
            self.fields['modelo_documento'].limit_choices_to = {'pk_uuid': self.document_object.pk_uuid}
            self.fields['modelo_documento'].initial = self.document_object

            self.fields['modelo_documento'].widget.attrs.update(
                {'not-is-model': 'true' if not self.document_object.eh_modelo else False,
                 'data-preview': True,
                 'disabled': True
                 }
            )

    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumento.objects.all(),
        widget=autocomplete.ModelSelect2(url='documentos:tipodocumento-autocomplete', ),

    )

    modelo_documento = ModeloDocumentoTemplateModelChoiceField(
        label='Modelo de Documento',
        to_field_name='pk_uuid',
        required=False,
        queryset=Documento.admin_objects.none(),

    )

    def clean_modelo_documento(self):
        return self.document_object


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


def create_form_class_adicionar_assinantes(document_object):
    url_autocomplete = reverse('documentos:grupos_ainda_nao_assinantes_do_documento_autocomplete',
                               kwargs={'slug': document_object.pk_uuid})

    class AdicionarAssinantesForm(BootstrapFormInputMixin, forms.Form):

        def __init__(self, *args, **kwargs):
            grupo_para_adicionar_queryset = kwargs.pop('grupo_para_adicionar_queryset')
            super(AdicionarAssinantesForm, self).__init__(*args, **kwargs)
            self.fields['grupo_para_adicionar'].queryset = grupo_para_adicionar_queryset

        grupo_para_adicionar = GrupoModelMultipleChoiceField(
            label=get_djdocuments_backend().get_group_label(),
            queryset=get_djdocuments_backend().get_grupos(),
            widget=autocomplete.ModelSelect2Multiple(url=url_autocomplete)
        )

    return AdicionarAssinantesForm


class DocumetoValidarForm(BootstrapFormInputMixin, forms.Form):
    # id = forms.CharField()
    # codigo_crc = SplitedHashField(split_into=4)
    # codigo_crc = forms.CharField(widget=SplitWidget(), initial='ABCDABCDABCDABCD')
    # assinatura_hash = SplitedHashField2(label='Codigo CRC',
    #                                     initial='ABCDABCDABCDABCD'
    #                                     )
    assinatura_hash = SplitedHashField3(label='Codigo CRC',
                                        split_guide=(10, 10, 10, 10),
                                        # initial='AAAABBBCCDDDDDD'
                                        )
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(DocumetoValidarForm, self).__init__(*args, **kwargs)
        self.documento = None

    def clean_assinatura_hash(self):
        assinatura_hash = self.cleaned_data['assinatura_hash']
        assinatura_hash = "sha1$djdocumentos${}".format(assinatura_hash.lower())
        try:
            self.documento = Documento.objects.get(assinatura_hash=assinatura_hash)
        except Exception:
            raise forms.ValidationError(
                "O documento não é valido"
            )
        return assinatura_hash

    class Meta:
        model = Documento
        fields = ('assinatura_hash',)
        # def clean_codigo_crc(self):
        #     codigo_crc = self.cleaned_data.get('codigo_crc')
        #     print('codigo_crc:', codigo_crc)
        #     return codigo_crc


class FinalizarDocumentoForm(BootstrapFormInputMixin, DjDocumentsBackendMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        self.current_logged_user = kwargs.pop('current_logged_user')
        super(FinalizarDocumentoForm, self).__init__(*args, **kwargs)

    finalizado_por = UserModelChoiceField(
        label="Assinante",
        help_text="Selecione o usuário que irá finalizar o documento",
        # queryset=get_real_user_model_class().objects.all().order_by('username'),
        queryset=USER_MODEL.objects.all().order_by('username'),
        widget=ModelSelect2ForwardExtras(url='documentos:user-by-group-autocomplete', ),

    )
    password = forms.CharField(label="Senha",
                               help_text="Digite a senha do usuário atual",
                               widget=forms.PasswordInput())

    def clean_password(self):
        password = self.cleaned_data.get('password')
        valid = check_password(password, self.current_logged_user.password)
        if not valid:
            raise forms.ValidationError('Invalid password')

        return password


def create_form_class_assinar(assinatura, usuario_atualmente_logado=None):
    document_object = assinatura.documento
    usuario_atualmente_logado = None
    url_autocomplete = reverse('documentos:grupos_assinantes_do_documento_autocomplete',
                               kwargs={'slug': document_object.pk_uuid})
    djdocuments_backend = get_djdocuments_backend()
    grupos_ids = document_object.assinaturas.filter(esta_assinado=False).distinct('grupo_assinante').values_list(
        'grupo_assinante_id',
        flat=True)
    grupos = document_object.grupos_assinates.filter(id__in=grupos_ids).distinct()
    usuarios_grupo = djdocuments_backend.get_usuarios_grupo(assinatura.grupo_assinante)

    class AssinarDocumentoForm(BootstrapFormInputMixin, DjDocumentsBackendMixin, forms.ModelForm):
        # titulo = forms.CharField(max_length=500)]
        grupo_assinante = GrupoModelChoiceField(
            label=djdocuments_backend.get_group_label(),
            help_text="Selecione o {}".format(djdocuments_backend.get_group_label()),
            queryset=grupos,
            widget=autocomplete.ModelSelect2(url=url_autocomplete, forward=('grupo_assinante',)),
        )

        assinado_por = UserModelChoiceField(
            label="Assinante",
            help_text="Selecione o usuário que irá assinar o documento",
            # queryset=get_real_user_model_class().objects.all().order_by('username'),
            queryset=usuarios_grupo.order_by('username'),
            widget=ModelSelect2ForwardExtras(url='documentos:user-by-group-autocomplete',
                                             forward=('grupo_assinante',), clear_on_change=('grupo_assinante',)),

        )

        password = forms.CharField(label="Senha",
                                   help_text="Digite a senha do usuário selecionado",
                                   widget=forms.PasswordInput())

        error_messages = {
            'invalid_login': _("Please enter a correct %(username)s and password. "
                               "Note that both fields may be case-sensitive."),
            'inactive': _("This account is inactive."),
        }

        class Meta:
            model = Assinatura
            fields = ('grupo_assinante', 'assinado_por', 'password')

        def clean_grupo_assinante(self):
            if self.instance.grupo_assinante:
                return self.instance.grupo_assinante
            return self.cleaned_data['grupo_assinante']

        def clean_assinado_por(self):
            if self.instance.assinado_por:
                return self.instance.assinado_por
            assinado_por = self.cleaned_data.get('assinado_por')
            return assinado_por

        def clean_password(self):
            password = self.cleaned_data.get('password')
            if self.instance.assinado_por:
                user = self.instance.assinado_por
            else:
                user = self.cleaned_data.get('assinado_por')

            if user:
                valid = check_password(password, user.password)

                if not valid:
                    self.add_error('password', forms.ValidationError('Senha inválida para o assinante selecionado'))
            return password

        def __init__(self, *args, **kwargs):
            super(AssinarDocumentoForm, self).__init__(*args, **kwargs)
            self.fields['assinado_por'].initial = usuario_atualmente_logado
            if self.instance.grupo_assinante:
                users = self.djdocuments_backend.get_usuarios_grupo(self.instance.grupo_assinante)
                self.fields['grupo_assinante'] = GrupoModelChoiceField(
                    label=djdocuments_backend.get_group_label(),
                    help_text="Selecione o {}".format(djdocuments_backend.get_group_label()),
                    queryset=grupos,
                    initial=self.instance.grupo_assinante,
                )
                self.fields['grupo_assinante'].required = False
                self.fields['grupo_assinante'].widget.attrs.update(
                    {
                        'class': 'form-control disabled',
                        'readonly': True,
                        'disabled': 'disabled'
                    }
                )
                if self.instance.assinado_por:
                    print('entrou aqui')
                    self.fields['assinado_por'] = UserModelChoiceField(
                        label="Assinante",
                        help_text="Selecione o usuário que irá assinar o documento",
                        queryset=users.filter(username=self.instance.assinado_por.username),
                        initial=self.instance.assinado_por

                    )
                    self.fields['assinado_por'].required = False
                    # self.fields['assinado_por'].initial = self.instance.assinado_por
                    self.fields['assinado_por'].widget.attrs.update(
                        {
                            'class': 'form-control disabled',
                            'readonly': True,
                            'disabled': 'disabled'
                        }
                    )

    return AssinarDocumentoForm


def create_form_class_finalizar(document_object):
    url_autocomplete = reverse('documentos:grupos_assinantes_do_documento_autocomplete',
                               kwargs={'slug': document_object.pk_uuid})
    djdocuments_backend = get_djdocuments_backend()
    grupos = djdocuments_backend.get_grupo_model().objects.filter(pk=document_object.grupo_dono.pk)

    class AssinarDocumentoForm(BootstrapFormInputMixin, DjDocumentsBackendMixin, forms.Form):
        # titulo = forms.CharField(max_length=500)]
        grupo = forms.ChoiceField(
            label=djdocuments_backend.get_group_label(),
            help_text="Selecione a {}. Somente a Defensoria criadora do documento pode finaliza-lo".format(
                djdocuments_backend.get_group_label()),
            # queryset=get_grupo_assinante_model_class().objects.all(),
            choices=grupos,
            widget=autocomplete.ModelSelect2(url=url_autocomplete, forward=('grupo',)),
        )

        assinado_por = UserModelChoiceField(
            label="Assinante",
            help_text="Selecione o usuário que irá assinar o documento",
            # queryset=get_real_user_model_class().objects.all().order_by('username'),
            queryset=USER_MODEL.objects.all().order_by('username'),
            widget=ModelSelect2ForwardExtras(url='documentos:user-by-group-autocomplete',
                                             forward=('grupo',), clear_on_change=('grupo',)),

        )

        password = forms.CharField(label="Senha",
                                   help_text="Digite a senha do usuário selecionado",
                                   widget=forms.PasswordInput())

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

                if not grupo_escolhido_queryset:
                    pass
                    # raise backend.get_grupo_model.
                self.fields['grupo'] = GrupoModelChoiceField(
                    label=self.djdocuments_backend.get_group_label(),
                    help_text="Selecione a {}. Somente a Defensoria criadora do documento pode finaliza-lo".format(
                        djdocuments_backend.get_group_label()),
                    queryset=grupo_escolhido_queryset,
                    required=False,
                    empty_label=None,
                    initial=self.grupo_escolhido,
                    widget=forms.Select(attrs={'class': 'form-control', 'readonly': True, 'disabled': 'disabled'})
                )
                self.fields['assinado_por'].queryset = self.djdocuments_backend.get_usuarios_grupo(
                    self.grupo_escolhido)

        def clean_grupo(self):
            if self.grupo_escolhido:
                return self.grupo_escolhido
            return self.cleaned_data['grupo']

        def clean_assinado_por(self):
            assinado_por = self.cleaned_data.get('assinado_por')
            return assinado_por

        def clean_password(self):
            password = self.cleaned_data.get('password')
            user = self.cleaned_data.get('assinado_por')
            valid = check_password(password, user.password)
            if not valid:
                raise forms.ValidationError('Invalid password')

            return password

    return AssinarDocumentoForm


class TipoDocumentoForm(BootstrapFormInputMixin, forms.ModelForm):

    class Meta:
        model = TipoDocumento
        fields = '__all__'
