import bleach
from django.db import models
from django.template.defaultfilters import striptags
from django.utils.safestring import mark_safe


class RemoveHTMLTextField(models.TextField):
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        striped_str = striptags(value)
        return mark_safe(bleach.clean(striped_str))
