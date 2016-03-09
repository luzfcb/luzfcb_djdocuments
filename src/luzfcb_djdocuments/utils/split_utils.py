# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import collections

try:
    from django.utils import six
except ImportError:
    import six


def gsplit(string_to_split, split_guide, merge_last=True):
    """
    Retorna uma lista contendo string_to_split dividida conforme split_guide.
    split_guide devera conter uma lista com o numero de caracteres que voce quer que contenha
    cada item da lista retorno.

    Por exemplo: A string_to_split for 'AAAABB' e split_guide for (4, 2), a lista retorno sera ['AAAA', 'BB']

    Se merge_last for True e quantidade de caracteres de string_to_split for maior que tamanho da lista split_guide
    a quantidade excedente de caracteres sera mergeada no ultimo item da lista.

    Por exemplo: A string_to_split for 'AAAABBCC' e split_guide for (4, 2) e merge_last True, a lista retorno sera
    ['AAAA', 'BBCC'] e se merge_last for False, a lista retorno sera ['AAAA', 'BB', 'CC']

    :param string_to_split: String to split
    :param split_guide: a positive Tuple of integers greater than zero'
    :param merge_last
    :return: list

    >>> a = 'AAAABBBCCDDDD'
    >>> s = [4, 3, 2]
    >>> gsplit(a, s)
    ['AAAA', 'BBB', 'CCDDDD']
    >>> b = 'AAAABBBCC'
    >>> s = [4, 3, 2]
    >>> gsplit(b, s)
    ['AAAA', 'BBB', 'CC']
    >>> a = 'AAAABBBCCDDDD'
    >>> s = [4, 3, 2]
    >>> gsplit(a, s, False)
    ['AAAA', 'BBB', 'CC', 'DDDD']
    >>> c = 'AAAABBBCC'
    >>> s = [4, 3, 2, 'a']
    >>> gsplit(c, s)
    Traceback (most recent call last):
    AssertionError: Expected a Tuple of positive integers greater than zero
    >>> a = 'AAAABBBCCDDDD'
    >>> s = [4, 3, -2]
    >>> gsplit(a, s, False)
    Traceback (most recent call last):
    AssertionError: Expected a Tuple of positive integers greater than zero
    >>> s = [4, 3, -2]
    >>> gsplit(None, s, False)
    Traceback (most recent call last):
    AssertionError: Expected string_to_split
    >>> s = [4, 3, -2]
    >>> gsplit(s, s, False)
    Traceback (most recent call last):
    AssertionError: Expected string_to_split
    """

    assert isinstance(string_to_split, six.string_types), 'Expected string_to_split'
    assert isinstance(split_guide, collections.Iterable) and all(
        isinstance(x, int) and x > 0 for x in split_guide), 'Expected a Tuple of positive integers greater than zero'
    str_len = len(string_to_split)
    split_len = sum(split_guide)
    previous_i = 0
    i = 0
    l = []

    for qnt_chars in split_guide:
        last_sun = i + qnt_chars
        parte = string_to_split[i:last_sun]
        previous_i = i
        i = last_sun
        l.append(parte)
    if str_len > split_len:
        if merge_last:
            l[-1] = string_to_split[previous_i:]
        else:
            l.append(string_to_split[i:])
    return l
