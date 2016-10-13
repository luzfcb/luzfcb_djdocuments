========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov| |coveralls|
        | |landscape| |scrutinizer| |codacy| |codeclimate|
    * - package
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|


.. |coveralls| image:: https://coveralls.io/repos/github/luzfcb/luzfcb_djdocuments/badge.svg?branch=master
    :target: https://coveralls.io/github/luzfcb/luzfcb_djdocuments?branch=master
    :alt: Coveralls Coverage Status

.. |docs| image:: https://readthedocs.org/projects/luzfcb_djdocuments/badge/?style=flat
    :target: https://readthedocs.org/projects/luzfcb_djdocuments
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/luzfcb/luzfcb_djdocuments.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/luzfcb/luzfcb_djdocuments

.. |requires| image:: https://requires.io/github/luzfcb/luzfcb_djdocuments/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/luzfcb/luzfcb_djdocuments/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/luzfcb/luzfcb_djdocuments/coverage.svg?branch=master
    :alt: Codecov Coverage Status
    :target: https://codecov.io/github/luzfcb/luzfcb_djdocuments

.. |landscape| image:: https://landscape.io/github/luzfcb/luzfcb_djdocuments/master/landscape.svg?style=flat
    :target: https://landscape.io/github/luzfcb/luzfcb_djdocuments/master
    :alt: Code Quality Status

.. |codacy| image:: https://img.shields.io/codacy/a71897c2633843088927a0008fb14f12.svg?style=flat
    :target: https://www.codacy.com/app/luzfcb/luzfcb_djdocuments
    :alt: Codacy Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/luzfcb/luzfcb_djdocuments/badges/gpa.svg
   :target: https://codeclimate.com/github/luzfcb/luzfcb_djdocuments
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/luzfcb_djdocuments.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/luzfcb_djdocuments

.. |downloads| image:: https://img.shields.io/pypi/dm/luzfcb_djdocuments.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/luzfcb_djdocuments

.. |wheel| image:: https://img.shields.io/pypi/wheel/luzfcb_djdocuments.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/luzfcb_djdocuments

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/luzfcb_djdocuments.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/luzfcb_djdocuments

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/luzfcb_djdocuments.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/luzfcb_djdocuments

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/luzfcb/luzfcb_djdocuments/master.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/luzfcb/luzfcb_djdocuments/


.. end-badges

A very, very simple digital document editor

* Free software: BSD license

Installation
============

::

    pip install luzfcb_djdocuments

Documentation
=============

https://luzfcb_djdocuments.readthedocs.org/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

