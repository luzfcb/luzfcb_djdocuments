from __future__ import unicode_literals

from django.utils import six


class ReadOnlyFieldsMixin(object):
    readonly_fields = ()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        self.define_readonly_fields(self.fields)

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin, self).clean()

        for field_name, field in six.iteritems(self.fields):
            if self._must_be_readonly(field_name):
                cleaned_data[field_name] = getattr(self.instance, field_name)

        return cleaned_data

    def define_readonly_fields(self, field_list):

        fields = [field for field_name, field in six.iteritems(field_list)
                  if self._must_be_readonly(field_name)]

        map(lambda field: self._set_readonly(field), fields)

    def _all_fields(self):
        return not bool(self.readonly_fields)

    def _set_readonly(self, field):
        field.widget.attrs['disabled'] = 'true'
        field.required = False

    def _must_be_readonly(self, field_name):
        return field_name in self.readonly_fields or self._all_fields()


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
