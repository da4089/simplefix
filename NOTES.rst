Running the Unit Tests
======================

In my development environment, I have multiple virtualenvs.  I run
the tests in each of these environments before committing changes.

Once committed, the CI runs the tests in all supported interpreters.
It will build pull-request branches also.  CI will email your commit
address the results of its build.

To run tests from a local shell, I use:

.. code-block:: bash

   env PYTHONPATH=. python test/all.py

You should expect to see a DeprecationWarning about `append_time()`, but
otherwise all 90 tests passing (that number might increase).

To run just one test case, pass the class name as an additional parameter:

.. code-block:: bash

   env PYTHONPATH=. python test/all.py ParserTest

To run just a single test, pass the test case class and method name:

.. code-block:: bash

   env PYTHONPATH=. python test/all.py ParserTest.test_raw_data


Publishing a Release
====================

* Check the setup.py version.
* Check doc/conf.py version (search for "release =").
* Update doc/changes.rst using commit log.
* Commit and push everything.
* Activate the 3.6 venv (to get twine, wheel, etc)
* Run: rm -rf dist
* Run: python setup.py sdist
* Run: python setup.py bdist_wheel --universal
* Run: twine upload dist/*
* Run: git tag v$VERSION
* Run: git push --tags
* Go to GitHub and make a release
* Go to ReadTheDocs and rebuild to pick up new version
* Bump the setup.py version for next time, and commit.

