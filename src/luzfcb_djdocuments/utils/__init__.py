# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from django.conf import settings
from django.utils import six
from django.utils.http import urlencode, urlunquote
from django.utils.six.moves.urllib.parse import parse_qsl, urlparse, urlunsplit

__all__ = (
    'add_querystrings_to_url',
)


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


try:
    from urllib.request import pathname2url
    from urllib.parse import urljoin
except ImportError:  # Python2
    from urllib import pathname2url
    from urlparse import urljoin


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
