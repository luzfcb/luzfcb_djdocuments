# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from dal import autocomplete
from django import forms
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

from .models import Assinatura, Documento, TipoDocumento
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
from .utils import get_grupo_assinante_backend, get_grupo_assinante_model_class
from .utils.module_loading import get_real_user_model_class
from .widgets import CkeditorTextAreadWidget, ModelSelect2ForwardExtras

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


class AssinarDocumentoForm(BootstrapFormInputMixin, forms.Form):
    # titulo = forms.CharField(max_length=500)]
    grupo = forms.ChoiceField(
        label=get_grupo_assinante_backend().get_group_label(),
        help_text="Selecione o {}".format(get_grupo_assinante_backend().get_group_label()),
        # queryset=get_grupo_assinante_model_class().objects.all(),
        widget=autocomplete.ModelSelect2(url='documentos:grupos-autocomplete', forward=('grupo',)),
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
        grupo_escolhido_pk = kwargs.get('grupo_escolhido_pk')
        if grupo_escolhido_pk:
            kwargs.pop('grupo_escolhido_pk')
        self.grupo_escolhido = None
        super(AssinarDocumentoForm, self).__init__(*args, **kwargs)

        if grupo_escolhido_pk:
            self.initial['assinado_por'] = self.current_logged_user
            backend = get_grupo_assinante_backend()
            # grupo_escolhido_queryset = get_grupo_assinante_backend().get_grupo(pk=grupo_escolhido_pk,
            #                                                                    use_filter=True)
            grupo_escolhido_queryset = backend.get_grupo(pk=grupo_escolhido_pk,
                                                                               use_filter=True)
            if not grupo_escolhido_queryset:
                pass
                # raise backend.get_grupo_model.
            self.grupo_escolhido = grupo_escolhido_queryset[0]
            self.fields['grupo'] = GrupoModelChoiceField(
                label=get_grupo_assinante_backend().get_group_label(),
                help_text="Selecione o {}".format(get_grupo_assinante_backend().get_group_label()),
                queryset=grupo_escolhido_queryset,
                required=False,
                empty_label=None,
                initial=self.grupo_escolhido,
                widget=forms.Select(attrs={'class': 'form-control', 'readonly': True, 'disabled': 'disabled'})
            )
            self.fields['assinado_por'].queryset = get_grupo_assinante_backend().get_usuarios_grupo(self.grupo_escolhido)

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
        # assinado_por = self.cleaned_data.get('assinado_por')
        #
        # # cria ou obten instancia de Assinatura para o usuario selecionado em  assinado_por
        # obj, created = Assinatura.objects.get_or_create(documento=documento,
        #                                                 assinado_por=assinado_por,
        #                                                 versao_numero=documento.versao_numero,
        #                                                 esta_ativo=True,
        #                                                 defaults={
        #                                                     'documento': documento,
        #                                                     'assinado_por': assinado_por,
        #                                                     'versao_numero': documento.versao_numero + 1,
        #                                                     'esta_ativo': True
        #                                                 }
        #                                                 )
        # if created:
        #     print("criado : {}".format(obj.assinado_por.username))
        # else:
        #     print("obtido")
        #
        # if not obj.esta_assinado:
        #     obj.assinar_documento()
        #
        # # cria assinatura
        # usuarios_assinantes = self.cleaned_data.get('incluir_assinantes')
        # for usuario_assinante in usuarios_assinantes:
        #     # Assinatura.objects.get
        #     obj, created = Assinatura.objects.get_or_create(documento=documento,
        #                                                     assinado_por=usuario_assinante,
        #                                                     versao_numero=documento.versao_numero,
        #                                                     defaults={
        #                                                         'documento': documento,
        #                                                         'assinado_por': usuario_assinante,
        #                                                         'versao_numero': documento.versao_numero + 1,
        #                                                         'esta_assinado': False
        #                                                     }
        #                                                     )
        #     if created:
        #         print("criado : {}".format(obj.assinado_por.username))
        #         # notificar usuario
        #     else:
        #         print("obtido")
        #
        # documento.assinar_documento(
        #     assinado_por=self.cleaned_data.get('assinado_por'),
        #     current_logged_user=self.current_logged_user
        # )
        #
        # print(self.cleaned_data.get('incluir_assinantes'))
        return documento