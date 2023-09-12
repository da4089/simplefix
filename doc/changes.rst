
Change Log
==========

v1.0.17 (2023-09-12)
--------------------
* Fix checksum calculation bug introduced in v1.0.16.  This will break
  any usage that relies on simplefix calculating the checksum value:
  most users will need to upgrade.

v1.0.16 (2023-09-08)
--------------------
* Add missing EXECTYPE constants
* Better conversion to string (#40)
* Better installation instructions (#45)
* Add testing for large (64 bit) integer values (#52)
* Fixed handling of IntEnum tag values (#56)
* Added testing for CPython 3.11 (Released: 2022-10-24)
* Dropped testing for Python 3.6 (EOL: 2021-12-31)

v1.0.15 (2022-02-17)
--------------------
* Add framework for parser options
* Add parsing error exceptions
* Support parsing of empty values (#34)
* Updated programmer's guide
* Added testing for CPython 3.10 (Released: 2021-10-04)
* Removed testing for:

  * CPython 2.6 (EOL: 2013-10-29)
  * CPython 2.7 (EOL: 2020-01-01)
  * CPython 3.3 (EOL: 2017-09-29)
  * CPython 3.4 (EOL: 2019-03-18)
  * CPython 3.5 (EOL: 2020-09-30)

v1.0.14 (2020-04-30)
--------------------
* Fix typo in constant
* Add additional tags

v1.0.13 (2020-02-19)
--------------------
* Allow configuration of alternative end-of-message indicators. This is
  useful for parsing log files or mangled FIX with a non-standard
  terminating tag.
* Added various tags and their values (thanks Christian Oudard).
* Added testing for CPython 3.8 (Released: 2019-10-14)
* Dropped testing for CPython 3.3 (EOL: 2017-09-29)

v1.0.12 (2018-11-26)
--------------------
* Fix parser issue when parsing a message where the data field length is
  parsed from one call to append, but the content field is appended and
  parsed later (ie. append, parse -> None, append, parse -> msg).

v1.0.11
-------
* *Never released*

v1.0.10 (2018-09-28)
--------------------
* Fix a few issues pointed out by LGTM.
* Added testing for CPython 3.7 (Released: 2018-06-27)

v1.0.9 (2018-02-16)
-------------------
* Added new remove() function to delete a field from a message
* Added new __str__() special function, useful for showing a message in
  logging or debugging.
* Linked to https://simplefix.readthedocs.io from the README, hopefully
  making the detailed docs more visible.
* Added more constant values from the FIX specifications.

v1.0.8 (2017-12-15)
-------------------
* Added support for Python2.6 to support RHEL6/CentOS6 which doesn't EOL
  until November 2020.
* Added support for in and not in tests for tag numbers in messages.
* Adding a field with a value of None will silently fail.
* Unless it's preceded by a length field, a data type value will be
  treated as a standard (string) value.

v1.0.7 (2017-11-13)
-------------------
* Some major changes to the use of strings (vs. bytes) for Python 3.x,
  with all received values now exported as bytes, and input values being
  transformed to bytes using UTF-8 encoding (from strings) and ASCII
  encoding for everything else. If you want to use a different encoding,
  transform to bytes yourself first, but you probably should be using
  the FIX DATA type for encoded values anyway?
* Also a major expansion/rewrite of date and time value handling. Added
  a bunch of method covering all the FIX date/time types properly. The
  existing append_time method is deprecated, in favour of more
  specifically named methods for UTC and local timezones, and datetime,
  date-only and time-only values.

v1.0.6 (2017-08-24)
-------------------
* Add support for adding "header" fields: they are inserted, starting at
  the beginning of the message, prior to any existing fields. This allows
  FIX header fields, for instance SendingTime(52), to be added after the
  body fields.

v1.0.5 (2017-07-19)
-------------------
* Fix error in timestamp formatting
* Improved documentation

v1.0.4 (2017-07-07)
-------------------
* Flag release as Production/Stable.
* Added handling of FIX 'data' type fields to the parser. Data fields can
  contain arbitrary data, including the SOH character, and were not
  previously supported.
* Adding testing for CPython 3.6 (Released: 2016-12-23)

v1.0.3 (2017-01-17)
-------------------
* Added ability to iterate over the fields in a message.
* More test coverage.

v1.0.2 (2016-12-10)
-------------------
* Changes to raw mode, now supported only for ``encode()``.
* Improved test coverage.

v1.0.1 (2016-12-08)
-------------------
* Added software license.

v1.0.0 (2016-12-07)
-------------------
* Initial release
