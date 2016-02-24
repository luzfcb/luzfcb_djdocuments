from __future__ import unicode_literals


class DjangoDocumentosException(Exception):
    """ Base Exception for all exceptions of this module. """
    pass


class NonDjangoModelSubclassException(DjangoDocumentosException):
    """ Base Exception for all exceptions of this module. """

    def __init__(self, klass):
        msg = '{}s not is subclass of django Model'.format(klass.__name__)
        super(NonDjangoModelSubclassException, self).__init__(msg)


class InvalidDotPathToModelException(DjangoDocumentosException):
    """ Base Exception for all exceptions of this module. """

    def __init__(self, string):
        msg = "The string '{}s' not contain a valid path to a django model subclass. The correct format is 'app_name.ModelName'".format(string)  # noqa
        super(InvalidDotPathToModelException, self).__init__(msg)
