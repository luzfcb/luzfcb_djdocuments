# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# import autocomplete_light
from captcha.fields import CaptchaField
# from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Submit
from dal import autocomplete
from django import forms
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _

# TODO: remove this ugly hack
try:
    from test_app.tests.samples_html import BIG_SAMPLE_HTML, CABECALHO, RODAPE, TITULO
except ImportError:
    BIG_SAMPLE_HTML = CABECALHO = RODAPE = TITULO = ''

from .models import Documento
from .utils.module_loading import get_real_user_model_class
from .widgets import SplitedHashField3


class ProdutoForm(forms.ModelForm):
    vlunitario = forms.DecimalField(max_digits=10, decimal_places=2, localize=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))


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
        return obj.get_full_name().title()


class AssinarDocumento(AssinarDocumentoHelperFormMixin, forms.ModelForm):
    assinado_por = UserModelChoiceField(
        queryset=get_real_user_model_class().objects.all().order_by('username'),
        widget=autocomplete.ModelSelect2(url='documentos:user-autocomplete')
    )

    password = forms.CharField(label="Sua senha",
                               widget=forms.PasswordInput)

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
        documento.assinar_documento(
            assinado_por=self.cleaned_data.get('assinado_por'),
            current_logged_user=self.current_logged_user
        )
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


from .templatetags.luzfcb_djdocuments_tags import remover_tags_html


class TemplareModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return remover_tags_html(obj.titulo)


from .models import DocumentoTemplate


class CriarDocumentoForm(forms.Form):
    titulo = forms.CharField(max_length=500)
    template_documento = TemplareModelChoiceField(
        queryset=DocumentoTemplate.objects.all(),
        # widget=autocomplete.ModelSelect2(url='documentos:user-autocomplete')
        widget=forms.RadioSelect
    )
