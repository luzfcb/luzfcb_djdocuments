# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import collections
import re
from pprint import pprint

from dal import autocomplete
from django import forms
from django.core.validators import RegexValidator
from django.forms import widgets
from django.utils.translation import ugettext

from .utils.split_utils import gsplit

ascii_e_numeros_re = re.compile(r'^[a-zA-Z0-9]+\Z')

validate_ascii_e_numeros = RegexValidator(ascii_e_numeros_re,
                                          ugettext('Conteudo invalido. Deve conter somente letras e numeros'),
                                          'invalid')


class SplitWidget(widgets.MultiWidget):

    def __init__(self, attrs=None, split_into=4, value_size=None, value=None, fields_max_length=None):
        assert isinstance(split_into, int) and split_into > 0, '"split_into" parameter expect a positive integer'
        self.split_into = split_into
        # assert isinstance(value_size, int) and split_into > -1, '"value_size" parameter expect a positive integer'
        self.value_size = value_size or self.split_into
        value = value

        attrs = attrs or {}
        attrbs = []
        fields_max_length = fields_max_length or [len(value[i: i + self.split_into]) for i in
                                                  range(0, len(value), self.split_into)]
        for max_length in fields_max_length:
            at = attrs.copy()
            pattern = r'^[A-Za-z0-9]{{{minlength},{maxlength}}}$'.format(minlength=max_length, maxlength=max_length)

            at.update({
                'maxlength': max_length,
                'minlength': max_length,
                # 'data-minlength': max_length,
                'pattern': pattern,
                # 'title': 'Insira o valor correto uai'
            })
            attrbs.append(at)

        _widgets = [widgets.TextInput(attrs=atb) for atb in attrbs]
        super(SplitWidget, self).__init__(widgets=_widgets, attrs=attrs)
        # print(self.__class__.__name__)
        # pprint(dir(self), depth=2)
        # pprint(dir(self), depth=2)

    def decompress(self, value):
        if value:
            return [value[i: i + self.split_into] for i in range(0, len(value), self.split_into)]
        return [None for __ in range(0, self.value_size, self.split_into)]

    def value_from_datadict(self, data, files, name):
        print('value_from_datadict:')
        pprint(locals())
        return super(SplitWidget, self).value_from_datadict(data, files, name)


class SplitedHashField2(forms.MultiValueField):
    default_validators = [validate_ascii_e_numeros]

    # widget = SplitWidget

    def __init__(self, split_into=4, *args, **kwargs):
        assert isinstance(split_into, int) and split_into > 0, '"split_into" parameter expect a positive integer'
        kwargs.pop('widget', None)  # descarta qualquer widget
        value = kwargs.get('initial', None) or 'A' * split_into
        self.value_size = len(value)
        self.split_into = split_into

        fields_max_length = [len(value[i: i + self.split_into]) for i in
                             range(0, len(value), self.split_into)]
        regexes = {}
        fields = []
        for max_length in fields_max_length:
            if not regexes.get(max_length):
                regexes[max_length] = re.compile(
                    r'^[A-Za-z0-9]{{{minlength},{maxlength}}}$'.format(minlength=max_length, maxlength=max_length))
            fields.append(forms.RegexField(regex=regexes[max_length], max_length=max_length, min_length=max_length))

        self.widget = SplitWidget(split_into=self.split_into, value_size=self.value_size, value=value,
                                  fields_max_length=fields_max_length)
        super(SplitedHashField2, self).__init__(fields, *args, **kwargs)
        print('')

        # if self.max_length is not None:
        #     self.validators.append(validators.MinLengthValidator(int(self.max_length)))
        # if self.min_length is not None:
        #     self.validators.append(validators.MaxLengthValidator(int(self.min_length)))
        # print(self.__class__.__name__)
        # pprint(dir(self), depth=2)

    def clean(self, value):
        pre_clean = super(SplitedHashField2, self).clean(value)
        print('clean', value)
        # if pre_clean:
        #     for data in pre_clean:
        #         if data and len(data) < self.split_into:
        #             raise ValidationError(self.error_messages['required'], code='required')
        #         else:
        #             raise ValidationError(self.error_messages['required'], code='required')
        return ''.join(pre_clean)

    def to_python(self, value):
        print('pre_to_python:', value)
        # value = ''.join(value)
        ret = super(SplitedHashField2, self).to_python(value)
        print('to_python:', value)
        return ret

    def validate(self, value):
        print('validate:', value)
        # if value:
        #     for data in value:
        #         if data and len(data) < self.split_into:
        #             raise ValidationError(self.error_messages['required'], code='required')
        #         else:
        #             raise ValidationError(self.error_messages['required'], code='required')
        return super(SplitedHashField2, self).validate(value)

    def compress(self, data_list):
        return ''.join(data_list)


class SplitWidget2(widgets.MultiWidget):

    def __init__(self, attrs=None, split_guide=None, merge_last=True, value=None):
        assert isinstance(split_guide, collections.Iterable) and all(
            isinstance(x, int) and x > 0 for x in
            split_guide), 'Expected a Tuple of positive integers greater than zero'  # noqa
        self.split_guide = split_guide
        self.merge_last = merge_last
        self.split_len = len(self.split_guide)
        attrs = attrs or {}
        attrbs = []

        for max_length in self.split_guide:
            at = attrs.copy()
            pattern = r'^[A-Za-z0-9]{{{minlength},{maxlength}}}'.format(minlength=max_length, maxlength=max_length)

            at.update({
                'maxlength': max_length,
                'minlength': max_length,
                # 'data-minlength': max_length,
                'pattern': pattern,
                # 'title': 'Insira o valor correto uai'
            })
            attrbs.append(at)

        _widgets = [widgets.TextInput(attrs=atb) for atb in attrbs]
        super(SplitWidget2, self).__init__(widgets=_widgets, attrs=attrs)
        # print(self.__class__.__name__)
        # pprint(dir(self), depth=2)
        # pprint(dir(self), depth=2)

    def decompress(self, value):
        if value:
            return gsplit(value, self.split_guide, self.merge_last)
        return [None for __ in self.split_guide]


class SplitedHashField3(forms.MultiValueField):
    default_validators = [validate_ascii_e_numeros]

    # widget = SplitWidget

    def __init__(self, split_guide=None, merge_last=True, *args, **kwargs):
        # assert isinstance(split_guide, int) and split_guide > 0, '"split_guide" parameter expect a positive integer'
        self.split_guide = split_guide
        self.split_len = len(self.split_guide)
        kwargs.pop('widget', None)  # descarta qualquer widget
        value = kwargs.get('initial', None) or 'A' * self.split_len
        self.value_size = len(value)
        print('SplitedHashField3:', value)
        regexes = {}
        fields = []
        for max_length in self.split_guide:
            if not regexes.get(max_length):
                regexes[max_length] = re.compile(
                    r'^[A-Za-z0-9]{{{minlength},{maxlength}}}$'.format(minlength=max_length, maxlength=max_length))
            fields.append(forms.RegexField(regex=regexes[max_length], max_length=max_length, min_length=max_length))

        self.widget = SplitWidget2(split_guide=self.split_guide, merge_last=False, attrs={'class': 'auto_next'})
        super(SplitedHashField3, self).__init__(fields, *args, **kwargs)
        print('')

    def clean(self, value):
        pre_clean = super(SplitedHashField3, self).clean(value)
        print('SplitedHashField3:', 'clean', value)
        # if pre_clean:
        #     for data in pre_clean:
        #         if data and len(data) < self.split_into:
        #             raise ValidationError(self.error_messages['required'], code='required')
        #         else:
        #             raise ValidationError(self.error_messages['required'], code='required')
        return ''.join(pre_clean)

    def to_python(self, value):
        print('pre_to_python:', value)
        # value = ''.join(value)
        ret = super(SplitedHashField3, self).to_python(value)
        print('to_python:', value)
        return ret

    def prepare_value(self, value):
        return super(SplitedHashField3, self).prepare_value(value)

    def validate(self, value):
        print('SplitedHashField3', 'validate:', value)
        # if value:
        #     for data in value:
        #         if data and len(data) < self.split_into:
        #             raise ValidationError(self.error_messages['required'], code='required')
        #         else:
        #             raise ValidationError(self.error_messages['required'], code='required')
        return super(SplitedHashField3, self).validate(value)

    def compress(self, data_list):
        return ''.join(data_list)


class ForwardExtrasMixin(object):

    def __init__(self, url=None, forward=None, clear_on_change=None, *args, **kwargs):
        self.clear_on_change = clear_on_change
        super(ForwardExtrasMixin, self).__init__(url, forward, *args, **kwargs)

    def build_attrs(self, *args, **kwargs):
        attrs = super(ForwardExtrasMixin, self).build_attrs(*args, **kwargs)

        if self.clear_on_change is not None and self.forward is not None:
            values = set(self.clear_on_change).intersection(self.forward)
            if values:
                attrs.setdefault('data-autocomplete-light-clear-on-change',
                                 ','.join(values))
        return attrs

    class Media:
        """Automatically include static files for the admin."""

        js = (
            'autocomplete_light/select2-clear-on-change.js',
        )


class ModelSelect2ForwardExtras(ForwardExtrasMixin, autocomplete.ModelSelect2):
    pass


class ModelSelect2MultipleForwardExtras(ForwardExtrasMixin, autocomplete.ModelSelect2Multiple):
    pass
