Parsing Messages
----------------

To parse a FIX message, first create an instance of the FixParser class.

.. index:: FixParser
.. code-block:: python
    :linenos:

    parser = simplefix.FixParser()

.. INDEX:: append_buffer, get_message, FixMessage

To extract FIX messages from a byte buffer, such as that received from a
socket, you should append it to the internal reassembly buffer using
``append_buffer()`` .  At any time, you can call ``get_message()`` : if there's
no complete message in the parser's internal buffer, it'll return ``None``,
otherwise, it'll return a ``FixMessage`` instance.

.. code-block:: python
    :linenos:

    parser.append_buffer(response_from_socket)
    message = parser.get_message()

.. index:: count, get

Once you've received a ``FixMessage`` from ``get_message()``, you can: check
the number of fields with ``count()``, retrieve the value of a field using
``get()`` or the built-in ``[ ]`` syntax, or iterate over all the fields
using ``for ... in ...``.

.. code-block:: python
    :linenos:

    message.count(49)
    >>> 1

    message.get(35)
    >>> 'A'

    message["35"]
    >>> 'A'

.. index:: repeating group

Members of repeating groups can be accessed using ``get(tag, nth)``, where the
"nth" value is an integer indicating the number of the group to use (note
that the first group is number one, not zero).

.. code-block:: python
    :linenos:

    message = get(9061, 2)
    >>> 22

Parser Options
..............

.. index:: options

By default, the parser is quite forgiving, and will attempt to extract FIX
messages from the supplied buffer ignoring strict adherence to the standard.

In some cases however, it can be useful to instruct the parser to be more or
less strict in particular ways, depending on the protocol implementation
you're dealing with.

The parser's constructor accepts several different keyword arguments,
each controlling a specific aspect of the parser's behaviour.  These options
can also be configured using individual functions on the parser object.

Empty Values
~~~~~~~~~~~~

The FIX standards explicitly prohibit the use of empty (zero-length)
values.  In practice however, these are sometimes seen, and this option
allows them to be parsed.

For example, a message like

.. code-block::
    :linenos:

    ...|TAG1=VAL1|TAG2=|TAG3=VAL3|...

.. index:: EmptyValueError

would, by default, raise the ``EmptyValueError`` exception.  This option
prevents that exception, and returns an empty string value instead.

.. index:: FixParser, allow_empty_values

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser(allow_empty_values=True)

or

.. index:: FixParser, set_allow_empty_values

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser()
    parser.set_allow_empty_values(True)

Missing BeginString
~~~~~~~~~~~~~~~~~~~
The *BeginString(8)* tag is required by the standard to be the first field
of all messages: always present, and always first.  By default, the
parser ensures that this is the case.   This option disables that check.

.. index:: FixParser, allow_missing_begin_string, BeginString

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser(allow_missing_begin_string=True)

or

.. index:: FixParser, set_allow_missing_begin_string, BeginString

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser()
    parser.set_allow_missing_begin_string(True)

Note: see Strip Fields Before BeginString below for restrictions on
combining that with this option.

Strip Fields Before BeginString
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In some cases, message reception timestamps, inbound/outbound
direction flags, or other data might be encoded as "FIX" fields
prior to the *BeginString(8)*.  This option instructs the parser to
discard any fields found before the *BeginString(8)* when parsing.

.. index:: FixParser, strip_fields_before_begin_string, BeginString

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser(strip_fields_before_begin_string=True)

or

.. index:: FixParser, set_strip_fields_before_begin_string, BeginString

.. code-block:: python
    :linenos:

    parser = simplefix.FixParser()
    parser.set_strip_fields_before_begin_string(True)

.. index:: allow_missing_begin_string

Note: this option cannot be combined with
``allow_missing_begin_string`` as it requires a *BeginString(8)* field
to stop stripping.

Parser Errors
.............

.. index:: get_message, reassembly buffer

The ``get_message()`` method on the parser attempts to decode a FIX
message from its internal reassembly buffer.  It is not an error for
there to be no message or an incomplete message to be in the
reassembly buffer when it is called. In these cases, ``get_message()``
will simply return ``None``.

However, if the parser is unable to successfully decode a message, or
if any configured validation checks fail, the parser will raise an
exception to report the problem.

Possible exceptions are:

.. index:: allow_empty_values

.. py:exception:: EmptyValueError

    The parser read a field where the equals-sign was followed
    immediately by the field terminator byte (``SOH``).  This is
    not permitted by the FIX standard.

    Use the ``allow_empty_values`` parser option override this
    prohibition.

.. index:: BeginString, BodyLength, MsgType

.. py:exception:: FieldOrderError

    The FIX standard requires messages to contain some tags in
    a specific order and position.  For instance, *BeginString(8)*,
    *BodyLength(9)*, and *MsgType(35)* must occur in that order at
    the start of the message.

    This exception indicates that a tag was seen in an unexpected
    order or a tag was not seen where it was expected.

.. index:: stop_byte

.. py:exception:: IncompleteTagError

    When the parser is configured with ``stop_byte``, this exception
    indicates that the stop byte was read part-way through reading
    a tag -- that is, following a field terminator (``SOH``), and
    one or more tag digits, but before the equals sign.

    This normally indicates a corrupted message.

.. index:: remove_raw

.. py:exception:: RawLengthNotNumberError

    Raw data is encoded using two fields: a length field
    followed by the value field.  This exception indicates that
    a field whose tag number is registered as being a raw data
    *length* field was parsed, but that its value could not be
    decoded as a positive integer as expected.

    Usually, this means that the message being parsed uses a tag
    number that the FIX standard reserves as a raw data length
    field, but is here being used for another purpose.

    See ``simplefix.FixParser.remove_raw()`` for a way to change
    the set of tag numbers expected to be raw data lengths and
    values.

.. py:exception:: TagNotNumberError

    A field was parsed where the tag value, between the previous
    field terminator byte (``SOH``) and the equals-sign, could not be
    converted to a positive integer.

    This normally results from a corrupted message, often during
    development but usually rare in production.  It might suggest
    problems reassembling the byte stream from the socket layer.
