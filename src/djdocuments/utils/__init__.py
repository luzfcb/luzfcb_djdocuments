# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from django.apps import apps
from django.conf import settings
from django.utils import six
from django.utils.http import urlencode, urlunquote
from django.utils.six.moves.urllib.parse import parse_qsl, urlparse, urlunsplit

from .module_loading import import_member

try:
    from urllib.request import pathname2url
    from urllib.parse import urljoin
except ImportError:  # Python2
    from urllib import pathname2url
    from urlparse import urljoin

__all__ = (
    'InvalidDjDocumentsBackendException',
    'get_djdocuments_backend',
    'get_grupo_assinante_model_str',
    'get_grupo_assinante_model_class',
    'get_grupo_assinante_app_name_str',
    'add_querystrings_to_url',
    'intercalar',
    'pathname2fileurl',
    'make_absolute_paths',
    'admin_method_attributes',
)


class InvalidDjDocumentsBackendException(Exception):
    pass


def get_djdocuments_backend(*args, **kwargs):
    from ..settings import DJDOCUMENT
    backend_str = DJDOCUMENT['BACKEND']
    try:
        BackendClass = import_member(backend_str)
    except AttributeError as e:
        raise InvalidDjDocumentsBackendException(
            '\nthe selected backend not exist on path: {}\n you current configuration is:\n{}'.format(backend_str,
                                                                                                      DJDOCUMENT))
    else:
        return BackendClass(*args, **kwargs)


def get_grupo_assinante_model_str():
    from ..settings import DJDOCUMENT
    return DJDOCUMENT['GRUPO_ASSINANTE_MODEL']


def get_grupo_assinante_model_class():
    return apps.get_model(get_grupo_assinante_model_str())


def get_grupo_assinante_app_name_str():
    return get_grupo_assinante_model_class()._meta.app_label


def add_querystrings_to_url(url, querystrings_dict):
    uri = url

    while True:
        dec = urlunquote(uri)
        if dec == uri:
            break
        uri = dec

    parsed_url = urlparse(urlunquote(uri))

    current_params = dict(parse_qsl(parsed_url.query))
    current_params.update(
        querystrings_dict
    )

    parsed_params = {
        key: (lambda x: x, urlunquote)[isinstance(value, six.string_types)](value)
        for key, value in six.iteritems(current_params)
    }

    from pprint import pprint
    encoded_params = urlencode(parsed_params)
    pprint(parsed_params)

    # print('uri:', uri)

    new_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path.rstrip('\n\r').lstrip('\n\r'),
                          encoded_params, parsed_url.fragment))
    # print('new_url:', new_url)

    return new_url


def intercalar(string, a_cada=4, caracter="."):
    assert isinstance(string, six.string_types) and isinstance(caracter, six.string_types), 'Expected string'
    assert isinstance(a_cada, int) and a_cada > 0, 'Expected positive integer'
    return caracter.join(string[i:i + a_cada] for i in list(six.moves.xrange(0, len(string), a_cada)))


def pathname2fileurl(pathname):
    """Returns a file:// URL for pathname. Handles OS-specific conversions."""
    return urljoin('file:', pathname2url(pathname))


def make_absolute_paths(content):
    """Convert all MEDIA files into a file://URL paths in order to
    correctly get it displayed in PDFs."""
    overrides = [
        {
            'root': settings.MEDIA_ROOT,
            'url': settings.MEDIA_URL,
        },
        {
            'root': settings.STATIC_ROOT,
            'url': settings.STATIC_URL,
        }
    ]
    has_scheme = re.compile(r'^[^:/]+://')

    for x in overrides:
        if not x['url'] or has_scheme.match(x['url']):
            continue

        if not x['root'].endswith('/'):
            x['root'] += '/'

        occur_pattern = '''["|']({0}.*?)["|']'''
        occurences = re.findall(occur_pattern.format(x['url']), content)
        occurences = list(set(occurences))  # Remove dups
        for occur in occurences:
            content = content.replace(occur,
                                      pathname2fileurl(x['root']) +
                                      occur[len(x['url']):])

    return content


def admin_method_attributes(**outer_kwargs):
    """ Wrap an admin method with passed arguments as attributes and values.
    DRY way of extremely common admin manipulation such as setting short_description, allow_tags, admin_order_field etc.
    # https://stackoverflow.com/a/12048244

    # usage
    # models.py
    class MyModel(models.Model):
       temperatura = models.FloatField()

    # admin.py
    @admin.site.register(MyModel)
    class ModelAdmin(admin.ModelAdmin):
        list_display = [
            '_custom_temperatura_column',
            'temperatura',
            'my_admin_method',
        ]
        @admin_method_attributes(short_description='Some Short Description', allow_tags=True)
        def my_admin_method(self, obj):
            return '''<em>obj.id</em>'''

        @admin_method_attributes(short_description='Minha temperatura legal', admin_order_field='temperatura')
        def _custom_temperatura_column(self, obj):
            return obj.temperatura

    """

    def method_decorator(func):
        for kw, arg in outer_kwargs.items():
            setattr(func, kw, arg)
        return func

    return method_decorator
