# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from dal import autocomplete
from django import forms
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

from .models import Assinatura, Documento, TipoDocumento
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
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


class CriarDocumentoForm(BootstrapFormInputMixin, forms.Form):
    # titulo = forms.CharField(max_length=500)]

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


class AssinarDocumentoForm(forms.ModelForm):
    assinado_por = UserModelChoiceField(
        label="Assinante",
        help_text="Selecione o usuário que irá assinar o documento",
        queryset=get_real_user_model_class().objects.all().order_by('username'),
        widget=autocomplete.ModelSelect2(url='documentos:user-autocomplete', attrs={'class': 'form-control'}),

    )

    password = forms.CharField(label="Senha",
                               help_text="Digite a senha do usuário selecionado",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    incluir_assinantes = UserModelMultipleChoiceField(
        required=False,
        label="Incluir assinantes e notificar",
        help_text="Incluir assinantes e notificar",
        queryset=get_real_user_model_class().objects.all().order_by('username'),
        widget=autocomplete.ModelSelect2Multiple(url='documentos:user-autocomplete',
                                                 attrs={'class': 'form-control'},
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
        super(AssinarDocumentoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Documento
        # fields = '__all__'
        fields = ('assinado_por',)

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
