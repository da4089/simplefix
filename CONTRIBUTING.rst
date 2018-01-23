
============
Contributing
============

Contributions to this project are very welcome!

It's a pretty simple project, so there's not a lot of structure.  While
contributions of code, documentation, examples, etc, are great, just pointing
out issues, weaknesses, missing features, possible enhancements, etc, is
really helpful and very welcome too!

Following these guidelines helps to communicate that you respect the
time of the developers managing and developing this open source project.
In return, they should reciprocate that respect in addressing your issue,
assessing changes, and helping you finalize your pull requests.

Issues
======

The best way to ask a question, suggest a change, or whatever really, is
to create an issue on
`GitHub: <https://github.com/da4089/simplefix/issues/new>_`.

If you don't get a response within a day (or maybe two), feel free to
email me at d+simplefix@0x1.org.

Pull Requests
=============

Code or documentation changes should be submitted as a pull request
against the master branch.

Ground Rules
------------

* Ensure all code works across Python 2.6 and 2.7, 3.3, 3.4, 3.5 and 3.6.
  Maintaining support for 2.6 is probably the hardest part of this, but
  until RHEL6 / CentOS6 is no longer supported, its default interpreter
  will remain 2.6, and we'd like to continue to support it.

  There's some concessions to this rule in the unit tests, where the
  unittest module in 2.6 lacks a lot of useful features.  But core you'll
  see that the core code goes to some effort to maintain 2.6 compatibily.

* Ensure all code is cross-platform: Linux, Windows and MacOS.  While it
  Normally shouldn't matter, at least Ubuntu and Red Hat/CentOS Linuxes
  must be supported (ideally, any Unix-like system should work fine).

* You must have the right to donate your changes to the project.  This
  is normally only an issue if you're employed full-time as a programmer,
  but it's your responsibility to make sure you own your contributions,
  and can donate them to the project under the MIT license.

* The goal of this project is to remain **simple**.  Large or complicated
  feature additions might be better developed as an independent project
  that uses _simplefix_, rather than part of _simplefix_ itself.

Continual Integration
---------------------

The project uses `TravisCI <https://travis-ci.org>_` (thanks Travis
people!) to automatically build and test changes.

Check the Travis CI `dashboard <https://travis-ci.org/da4089/simplefix>_`
for current build status.

Coding Style
-------------

Python code should be PEP8 compatible.  I generally use PyCharm to catch
things that don't adhere to this standard.  See Preferences, Editor,
Inspections and turn on both the PEP8 options (syntax and naming).

Stylistic issues are monitored using `Landscape <https://landscape.io>_`
(thanks Landscape!).

See the project's `dashboard <https://landscape.io/github/da4089/simplefix>_`
for details, and please try to maintain or enhance the Landscape score
on any new submissions.

Unit Tests and Coverage
-----------------------

The unit tests use the standard library's 'unittest' module.  Code
coverage is monitored using `Coveralls <https://coveralls.ui>_`
(thanks Coveralls people as well!).

See the project `dashboard <https://coveralls.io/github/da4089/simplefix>_`
for details.  Submissions should always aim to maintain or improve test
coverage, but there's no need for crazy contortions to get to 100%: just
be reasonable about covering things that can actually happen.


Finally, is anything's unclear or you're uncertain or would like to chat
about something before diving in, please feel free to reach out by email
to d+simplefix@0x1.org.

Thanks!