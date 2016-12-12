simplefix
=========

|  |Build Status|  |Code Health|  |Coverage|  |PyPI|  |Python|

Introduction
------------

`FIX <http://www.fixtradingcommunity.org/pg/structure/tech-specs/fix-protocol>`_
(Financial Information eXchange) Protocol is a widely-used,
text-based protocol for interaction between parties in financial
trading.  Banks, brokers, clearing firms, exchanges, and other general
market participants use FIX protocol for all phases of electronic
trading.

Typically, a FIX implementation exists as a FIX Engine: a standalone
service that acts as a gateway for other applications (matching
engines, trading algos, etc) and implements the FIX protocol.  The
most popular Open Source FIX engine is probably one of the versions of
QuickFIX.

This package provides a *simple* implementation of the FIX
application-layer protocol.  It does no socket handling, and does not
implement FIX recovery or any message persistence.  It support the
creation, encoding, and decoding of FIX messages.

Licence
-------

The module is licensed under the `MIT license <https://opensource.org/licenses/MIT>`_.
While this is not legal advice, in short this means you're free to do
whatever you like with this code, with the exception of claiming you
wrote it.

Usage
-----



Contributing
------------

Comments, suggestions, bug reports, bug fixes -- all contributions to
this project are welcomed.  See the project's `GitHub
<https://github.com/da4089/simplefix>`_ page for access to the latest
source code, and please open an `issue
<https://github.com/da4089/simplefix/issues>`_ for comments,
suggestions, and bugs.



.. |Build Status| image:: https://travis-ci.org/da4089/simplefix.svg?branch=master
    :target: https://travis-ci.org/da4089/simplefix
    :alt: Build status
.. |Code Health| image:: https://landscape.io/github/da4089/simplefix/master/landscape.svg?style=flat
    :target: https://landscape.io/github/da4089/simplefix/master
    :alt: Code Health
.. |Coverage| image:: https://coveralls.io/repos/github/da4089/simplefix/badge.svg?branch=master
    :target: https://coveralls.io/github/da4089/simplefix?branch=master
    :alt: Coverage
.. |PyPI| image:: https://img.shields.io/pypi/v/simplefix.svg
    :target: https://pypi.python.org/pypi/simplefix
    :alt: PyPI
.. |Python| image:: https://img.shields.io/pypi/pyversions/simplefix.svg
    :target: https://pypi.python.org/pypi/simplefix
    :alt: Python
