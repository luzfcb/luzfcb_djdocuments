# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from captcha.fields import CaptchaField
from dal import autocomplete
from django import forms
from django.contrib.auth.hashers import check_password
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import Assinatura, Documento, TipoDocumento
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
from .utils import get_grupo_assinante_backend, get_grupo_assinante_model_class
from .utils.module_loading import get_real_user_model_class
from .widgets import CkeditorTextAreadWidget, ModelSelect2ForwardExtras, SplitedHashField3

# TODO: remove this ugly hack
try:
    from test_project.test_app.tests import BIG_SAMPLE_HTML, CABECALHO, RODAPE, TITULO
except ImportError:
    BIG_SAMPLE_HTML = CABECALHO = RODAPE = TITULO = ' '


class BootstrapFormInputMixin(object):
    def __init__(self, *args, **kwargs):
        super(BootstrapFormInputMixin, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            current_class_attr = field.widget.attrs.get('class', None)
            new_class_to_append = 'form-control'
            if current_class_attr:
                field.widget.attrs.update({
                    'class': '{} {}'.format(current_class_attr, new_class_to_append)
                })
            else:
                field.widget.attrs.update({
                    'class': '{}'.format(new_class_to_append)
                })


class DocumentoEditarForm(forms.ModelForm):
    cabecalho = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        initial=CABECALHO
    )
    titulo = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        initial=TITULO
    )
    conteudo = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        initial=BIG_SAMPLE_HTML
    )
    rodape = forms.CharField(
        widget=CkeditorTextAreadWidget,
        label='',
        initial=RODAPE
    )

    class Meta:
        model = Documento
        fields = ('cabecalho', 'titulo', 'conteudo', 'rodape')


class TipoDocumentoTemplateModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.titulo


class ModeloDocumentoTemplateModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        a = remover_tags_html(obj.titulo or 'Descricao modelo: {}'.format(obj.pk))
        print('ModeloDocumentoTemplateModelChoiceField:', a)
        return a


class GrupoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return get_grupo_assinante_backend().get_grupo_name(obj)


class CriarDocumentoForm(BootstrapFormInputMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user')
        super(CriarDocumentoForm, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['grupo'].queryset = get_grupo_assinante_backend().get_grupos_usuario(current_user)

    # titulo = forms.CharField(max_length=500)]
    grupo = GrupoModelChoiceField(
        label=get_grupo_assinante_backend().get_group_label(),
        queryset=get_grupo_assinante_model_class().objects.none()
    )

    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumento.objects.all(),

    )
    modelo_documento = ModeloDocumentoTemplateModelChoiceField(
        label='Modelo de Documento',
        queryset=Documento.admin_objects.all(),
        widget=ModelSelect2ForwardExtras(url='documentos:documentocriar-autocomplete',
                                         forward=('tipo_documento',),
                                         clear_on_change=('tipo_documento',)
                                         ),

    )

    assunto = forms.CharField(
        label='Assunto do Documento',
        max_length=70,

    )


class CriarModeloDocumentoForm(BootstrapFormInputMixin, forms.Form):
    # titulo = forms.CharField(max_length=500)
    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumento.objects.all(),

    )
    modelo_documento = ModeloDocumentoTemplateModelChoiceField(
        label='Modelo de Documento2',
        queryset=Documento.admin_objects.all(),
        # widget=autocomplete.ModelSelect2(url='documentos:documentocriar-autocomplete',
        #                                  forward=('tipo_documento',),
        #                                  #clear_on_change=('tipo_documento',)
        #                                  ),

    )

    template_descricao = forms.CharField(
        label='Descrição do Modelo',
        widget=forms.Textarea
    )


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


class AdicionarAssinantesForm(BootstrapFormInputMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        grupos_ja_adicionados = kwargs.pop('grupos_ja_adicionados')
        super(AdicionarAssinantesForm, self).__init__(*args, **kwargs)
        if grupos_ja_adicionados:
            self.fields['grupo_para_adicionar'].queryset = get_grupo_assinante_backend().get_grupos(
                excludes=grupos_ja_adicionados)

    grupo_para_adicionar = GrupoModelChoiceField(
        label=get_grupo_assinante_backend().get_group_label(),
        queryset=get_grupo_assinante_backend().get_grupos()
    )


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


def create_form_class_assinar(document_object):

    url_autocomplete = reverse('documentos:grupos-assinantes-do-documento',
                               kwargs={'slug': document_object.pk_uuid})
    grupos_ids = document_object.assinaturas.filter(assinado_por=None).values_list('grupo_assinante_id',
                                                                                   flat=True)
    grupos = document_object.grupos_assinates.filter(id__in=grupos_ids)

    class AssinarDocumentoForm(BootstrapFormInputMixin, forms.Form):
        # titulo = forms.CharField(max_length=500)]
        grupo = forms.ChoiceField(
            label=get_grupo_assinante_backend().get_group_label(),
            help_text="Selecione o {}".format(get_grupo_assinante_backend().get_group_label()),
            # queryset=get_grupo_assinante_model_class().objects.all(),
            choices=grupos,
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
