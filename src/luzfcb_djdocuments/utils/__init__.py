# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

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
