# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# import autocomplete_light
from captcha.fields import CaptchaField
# from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Submit
from dal import autocomplete
from django import forms
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

from .models import Assinatura, Documento, TipoDocumento
from .templatetags.luzfcb_djdocuments_tags import remover_tags_html
from .utils.module_loading import get_real_user_model_class
from .widgets import ModelSelect2ForwardExtras, SplitedHashField3

# TODO: remove this ugly hack
try:
    from test_project.test_app.tests import BIG_SAMPLE_HTML, CABECALHO, RODAPE, TITULO
except ImportError:
    BIG_SAMPLE_HTML = CABECALHO = RODAPE = TITULO = ' '


class ProdutoForm(forms.ModelForm):
    vlunitario = forms.DecimalField(max_digits=10, decimal_places=2, localize=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))


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


class SaveHelper(FormHelper):
    def __init__(self, form=None):
        super(SaveHelper, self).__init__(form)
        self.layout.append(Submit(name='save', value='Salvar'))
        self.form_method = 'post'
        self.form_show_errors = True
        self.render_required_fields = True
        self.render_unmentioned_fields = True


class SaveHelperFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(SaveHelperFormMixin, self).__init__(*args, **kwargs)
        self.helper = SaveHelper(self)


class RevertHelper(FormHelper):
    def __init__(self, form=None):
        super(RevertHelper, self).__init__(form)
        self.layout.append(Submit(name='revert', value='Reverter'))
        self.form_show_errors = True
        self.render_required_fields = True


class RevertHelperFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(RevertHelperFormMixin, self).__init__(*args, **kwargs)
        self.helper = RevertHelper(self)


class IsPopUpMixin(forms.Form):
    is_popup = forms.NullBooleanField(required=False, widget=forms.HiddenInput())


class NextFormMixin(forms.Form):
    proximo = forms.CharField(required=False, widget=forms.HiddenInput())


class DocumentoFormCreate(SaveHelperFormMixin, NextFormMixin, IsPopUpMixin, forms.ModelForm):
    # cabecalho = ckeditor_fields.RichTextField(blank=True)
    titulo = forms.CharField(max_length=500, widget=forms.HiddenInput())

    # conteudo = forms.CharField(widget=CKEditorWidget(), label='')

    # rodape = ckeditor_fields.RichTextField(blank=True)
    class Meta:
        model = Documento
        fields = '__all__'
        exclude = ['criado_por', 'modificado_por', 'esta_assinado']
        # widgets = {
        #     'conteudo': RedactorEditor()
        # }


class DocumentoFormUpdate(SaveHelperFormMixin, forms.ModelForm):
    # cabecalho = ckeditor_fields.RichTextField(blank=True)
    titulo = forms.CharField(max_length=500, widget=forms.HiddenInput())

    # conteudo = forms.CharField(widget=CKEditorWidget(), label='')

    # rodape = ckeditor_fields.RichTextField(blank=True)
    class Meta:
        model = Documento
        fields = '__all__'
        exclude = ['criado_por', 'modificado_por', 'esta_assinado']
        # widgets = {
        #     'conteudo': RedactorEditor()
        # }


class CkeditorWidgetNew(forms.Textarea):
    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {'data-djckeditor': 'true'}
        if attrs:
            default_attrs.update(attrs)
        super(CkeditorWidgetNew, self).__init__(default_attrs)


class DocumentoEditarForm(SaveHelperFormMixin, forms.ModelForm):
    cabecalho = forms.CharField(
        widget=forms.Textarea(attrs={'data-djckeditor': 'true'}),
        label='',
        initial=CABECALHO
    )
    titulo = forms.CharField(
        widget=forms.Textarea(attrs={'data-djckeditor': 'true'}),
        label='',
        initial=TITULO
    )
    conteudo = forms.CharField(
        widget=CkeditorWidgetNew,
        label='',
        initial=BIG_SAMPLE_HTML
    )
    rodape = forms.CharField(
        widget=forms.Textarea(attrs={'data-djckeditor': 'true'}),
        label='',
        initial=RODAPE
    )

    class Meta:
        model = Documento
        fields = ('cabecalho', 'titulo', 'conteudo', 'rodape')
        # fields = '__all__'
        # exclude = ['criado_por', 'modificado_por', 'esta_assinado']
        # widgets = {
        #     'conteudo': RedactorEditor()
        # }


class DocumentoRevertForm(RevertHelperFormMixin, forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'


class ValidarHelper(FormHelper):
    def __init__(self, form=None):
        super(ValidarHelper, self).__init__(form)
        self.layout.append(
            HTML("""<a class="btn btn-mini" onclick="refresh_captcha()"><i class="icon-refresh"></i> Refresh</a>""")

        )

        self.layout.append(Submit(name='validar', value='Verificar validade'))
        self.form_method = 'post'
        self.form_show_errors = True
        self.form_action = 'documentos:validar'
        self.render_required_fields = True
        self.render_unmentioned_fields = True


class ValidarHelperFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(ValidarHelperFormMixin, self).__init__(*args, **kwargs)
        self.helper = ValidarHelper(self)


class DocumetoValidarForm(ValidarHelperFormMixin, forms.Form):
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


# DocumetoValidarForm = parsleyfy(DocumetoValidarForm22)

class AssinarDocumentoHelper(FormHelper):
    def __init__(self, form=None):
        super(AssinarDocumentoHelper, self).__init__(form)
        # self.layout.append(
        #     HTML("""<a class="btn btn-mini" onclick="refresh_captcha()"><i class="icon-refresh"></i> Refresh</a>""")
        #
        # )
        self.layout.append(Submit(name='assinar', value='Assinar Documento'))
        self.form_id = 'form_assinar'
        self.form_method = 'post'
        self.form_show_errors = True
        # self.form_action = 'documentos:validar'
        self.render_required_fields = True
        self.render_unmentioned_fields = True


class AssinarDocumentoHelperFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(AssinarDocumentoHelperFormMixin, self).__init__(*args, **kwargs)
        self.helper = AssinarDocumentoHelper(self)


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return '{} ({})'.format(obj.get_full_name().title(), getattr(obj, obj.USERNAME_FIELD))


class AssinarDocumento(AssinarDocumentoHelperFormMixin, forms.ModelForm):
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
        super(AssinarDocumento, self).__init__(*args, **kwargs)

    class Meta:
        model = Documento
        # fields = '__all__'
        fields = ('assinado_por',)

    def clean_assinado_por(self):
        assinado_por = self.cleaned_data.get('assinado_por')
        print('AssinarDocumento: pk', assinado_por.pk, 'username', assinado_por.get_full_name())
        return assinado_por

    def clean_password(self):
        password = self.cleaned_data.get('password')
        user = self.cleaned_data.get('assinado_por')
        valid = check_password(password, user.password)
        if not valid:
            raise forms.ValidationError('Invalid password')

        return password

    def save(self, commit=True):
        documento = super(AssinarDocumento, self).save(False)
        assinado_por = self.cleaned_data.get('assinado_por')
        usuarios_assinantes = self.cleaned_data.get('incluir_assinantes')

        # cria ou obten instancia de Assinatura para o usuario selecionado em  assinado_por
        obj, created = Assinatura.objects.get_or_create(documento=documento,
                                                        assinado_por=assinado_por,
                                                        versao_numero=documento.versao_numero,
                                                        defaults={
                                                            'documento': documento,
                                                            'assinado_por': assinado_por,
                                                            'versao_numero': documento.versao_numero
                                                        }
                                                        )
        if created:
            print("criado : {}".format(obj.assinado_por.username))
        else:
            print("obtido")

        if not obj.esta_assinado:
            obj.assinar_documento()

        # cria assinatura
        for usuario_assinante in usuarios_assinantes:
            # Assinatura.objects.get
            obj, created = Assinatura.objects.get_or_create(documento=documento,
                                                            assinado_por=usuario_assinante,
                                                            versao_numero=documento.versao_numero,
                                                            defaults={
                                                                'documento': documento,
                                                                'assinado_por': usuario_assinante,
                                                                'versao_numero': documento.versao_numero,
                                                                'esta_assinado': False
                                                            }
                                                            )
            if created:
                print("criado : {}".format(obj.assinado_por.username))
                # notificar usuario
            else:
                print("obtido")

        documento.assinar_documento(
            assinado_por=self.cleaned_data.get('assinado_por'),
            current_logged_user=self.current_logged_user
        )
        print(self.cleaned_data.get('incluir_assinantes'))
        return documento


class RemoverAssinaturaDocumento(AssinarDocumentoHelperFormMixin, forms.ModelForm):
    # usuario_assinante = autocomplete_light.ModelChoiceField('UserAutocomplete')

    password = forms.CharField(label="Sua senha",
                               widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        self.current_logged_user = kwargs.pop('current_logged_user')
        super(RemoverAssinaturaDocumento, self).__init__(*args, **kwargs)

    class Meta:
        model = Documento
        fields = ('id',)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        user = self.cleaned_data.get('usuario_assinante')
        valid = check_password(password, user.password)
        if not valid:
            raise forms.ValidationError('Invalid password')

        return password

    def save(self, commit=True):
        documento = super(RemoverAssinaturaDocumento, self).save(False)

        documento.remover_assinatura_documento(current_logged_user=self.current_logged_user)
        return documento


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
