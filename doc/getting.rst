.. _getting:

Installation
============

simplefix has a few dependencies.  Firstly, it is known to run on
Python_ 3.8 through to 3.13.  It will not run on Python 3.5 or
earlier versions, including Python 2.7.

You can install it using pip_::

    $ pip install simplefix

or using easy_install_::

    $ easy_install simplefix

It's usually a good idea to install simplefix into a virtualenv, to avoid
issues with incompatible versions and system packaging schemes.

Getting the code
----------------

You can also get the code from PyPI_ or GitHub_. You can either clone the
public repository::

    $ git clone git://github.com/da4089/simplefix.git

Download the tarball::

    $ curl -OL https://github.com/da4089/simplefix/tarball/master

Or, download the zipball::

    $ curl -OL https://github.com/da4089/simplefix/zipball/master

Once you have a copy of the source you can install it into your site-packages
easily::

    $ python setup.py install



.. _easy_install: http://github.com/pypa/setuptools
.. _GitHub: https://github.com/da4089/simplefix
.. _Python: http://www.python.org/
.. _PyPI: https://pypi.org/project/simplefix/
.. _pip: http://www.pip-installer.org/
