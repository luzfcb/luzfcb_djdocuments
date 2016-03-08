# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import sys

__author__ = 'luzfcb'

__all__ = (
    'document',
)

PY3 = sys.version_info[0] == 3
if PY3:
    text_type = str
    range_func = range
else:
    text_type = unicode  # noqa
    range_func = xrange  # noqa

DOCUMENT_MAX_DIGITS = 8
DOCUMENT_VERSION_MAX_DIGITS = 3


def positive(n):
    n = int(n)
    assert n > 0, 'Expected positive integer'
    return n


def sequence(n, size):
    n = positive(n)  # adicionei por causa do caso de teste test_document_str_000000000000000000601_22
    assert len(str(n)) <= positive(size), 'Number dont fit size'
    return '{n:0>{size}}'.format(n=n, size=size)


def identifier(n, v):
    return 'v'.join((n, v))


def document_number(n):
    return sequence(n, DOCUMENT_MAX_DIGITS)


def document_version_number(v):
    return sequence(v, DOCUMENT_VERSION_MAX_DIGITS)


def document(n, v):
    return identifier(document_number(n), document_version_number(v))


if __name__ == "__main__":
    # import pytest
    #
    # pytest.main(args=['-vv', os.path.join(__file__)], )
    print(document(-10, 22))
