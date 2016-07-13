def coisa():
    return 'coisa'


def coisa_ex():
    raise Exception('ha')


import pytest


@pytest.fixture([1, 2, 13, 6])
def meu_model():
    class MeuModel(object):
        pass

    return MeuModel


def test_coisa():
    assert coisa() == 'coisa'


def test_coisa_except():
    with pytest.raises(Exception):
        coisa_ex()


def teste_meu(browser, meu_model):
    obj = meu_model()
    assert obj.__class__.__name__ == 'MeuModel'
