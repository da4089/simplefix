
=========
simplefix
=========

|  |Build Status|  |Docs|  |Code Health|  |Coverage|  |PyPI|  |Python|

Introduction
============

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
`QuickFIX <http://www.quickfixengine.org>`_.

This package provides a *simple* implementation of the FIX
application-layer protocol.  It does no socket handling, and does not
implement FIX recovery or any message persistence.  It supports the
creation, encoding, and decoding of FIX messages.

Licence
=======

The module is licensed under the `MIT license <https://opensource.org/licenses/MIT>`_.
While this is not legal advice, in short this means you're free to do
whatever you like with this code, with the exception of claiming you
wrote it.

Basic Usage
===========

Creating Messages
-----------------

To create a FIX message, first create an instance of the FixMessage class.

.. code-block:: python

    msg = simplefix.FixMessage()

You can then add fields to the message as required.  You should add the
standard header tags 8, 34, 35, 49, 52, and 56 to all messages.  For most
tags, using ``append_pair()`` is the easiest way to add a field to the message.
When adding a *UTCTimestamp*  value (ie, for tag 52) using
``append_utc_timestamp()`` will take care of the formatting for you.

``append_string()`` will decompose a "tag=value" string and add it as a proper
field; ``append_strings()`` will do the same for a sequence of "tag=value"
strings.   ``append_data()`` will correctly append a data field, setting the
length tag's value, and putting the value tag after the length in the
formatted message.

Once all fields are set, calling ``encode()`` will return a byte buffer
containing the correctly formatted FIX message, with fields in the required
order, and automatically added and set values for the BodyLength (9) and
Checksum (10) fields.

Note that if you want to manually control the ordering of all fields, the
value of the BodyLength or Checksum fields, there's a 'raw' flag to the
``encode()`` method that disables this functionality.  This is useful for
creating known-bad messages for testing purposes.

Parsing Messages
----------------

To extract FIX messages from a byte buffer, such as that received from a
socket, you should first create an instance of the ``FixParser`` class.  For
each byte string received, append it to the internal reassembly buffer using
``append_buffer()`` .  At any time, you can call ``get_message()`` : if there's
no complete message in the parser's internal buffer, it'll return None,
otherwise, it'll return a ``FixMessage`` instance.

Once you've received a ``FixMessage`` from ``get_message()`` , you can: check
the number of fields with ``count()`` , retrieve the value of a field using
``get()`` or the built-in "[ ]" syntax, or iterate over all the fields using
"for ... in ...".

Members of repeating groups can be accessed using ``get(tag, nth)``, where the
"nth" value is an integer indicating which occurrence of the tag to return
(note that the first occurrence is number one, not zero).


Contributing
============

Comments, suggestions, bug reports, bug fixes -- all contributions to
this project are welcomed.  See the project's `GitHub
<https://github.com/da4089/simplefix>`_ page for access to the latest
source code, and please open an `issue
<https://github.com/da4089/simplefix/issues>`_ for comments,
suggestions, and bugs.



.. |Build Status| image:: https://travis-ci.org/da4089/simplefix.svg?branch=master
    :target: https://travis-ci.org/da4089/simplefix
    :alt: Build status
.. |Docs| image:: https://readthedocs.org/projects/simplefix/badge/?version=latest
    :target: http://simplefix.readthedocs.io/en/latest/
    :alt: Docs
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
