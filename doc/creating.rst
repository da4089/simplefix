
Creating Messages
-----------------

To create a FIX message, first create an instance of the FixMessage class.

.. code-block:: python
    :linesnos:

    msg = simplefix.FixMessage()


You can then add fields to the message as required.  You should add the
standard header tags 8, 34, 35, 49, 52, and 56 to all messages, unless
you're deliberately creating a malformed message for testing or similar.

Simple Fields
.............

For most tags, using ``append_pair()`` is the easiest way to add a field
to the message.

.. code-block:: python

    message.append_pair(1, "MC435967")
    message.append_pair(54, 1)
    message.append_pair(44, 37.0582)

Note that any type of value can be used: it will be explicitly converted
to a string before encoding the message.

With a few exceptions, the message retains the order in which fields are
added.  The exceptions are that fields BeginString (8), Length (9),
MsgType (35), and Checksum (10) are encoded in their required locations,
regardless of what order they were added to the Message.

Header Fields
.............

The Message class does not distinguish header fields from body fields,
with one exception.

To enable fields to be added to the FIX header after body fields have
already been added, there's an optional keyword parameter to the
``append_pair()`` method (and other append field methods).  If this
``header`` parameter is set to ``True``, the field is inserted after
any previously added header fields, starting at the beginning of the
message.

This is normally used for setting things like MsgSeqNum (34) and
SendingTime (52) immediately prior to encoding and sending the message.

.. code-block:: python

    message.append_pair(8, "FIX.4.4")
    message.append_pair(35, 0)
    message.append_pair(49, "SENDER")
    message.append_pair(56, "TARGET")
    message.append_pair(112, "TR0003692")
    message.append_pair(34, 4684, header=True)
    message.append_time(52, header=True)

In the example above, field 34 would be inserted at the beginning of
the message.  After encoding, the order of fields would be: 8, 9, 35,
34, 52, 49, 56, 112, 10.

It's not necessary, but field 49 and 56 could also be written with
``header`` set ``True``, in which case, they'd precede 34 ane 52 when
encoded.

See ``append_time()`` below for details of that method.

Pre-composed Pairs
..................

In some cases, your FIX application might have the message content
as pre-composed "tag=value" strings.  In this case, as an optimisation,
the ``append_string()`` or ``append_strings()`` methods can be used.

.. code-block:: python

    BEGIN_STRING = "8=FIX.4.2"
    STR_SEQ = ["49=SENDER", "56=TARGET"]

    message.append_string(BEGIN_STRING, header=True)
    message.append_strings(STR_SEQ, header=True)

As with ``append_pair()``, note that these methods have an optional
keyword parameter to ensure that their fields are inserted before
body fields.

Timestamps
..........

The FIX protocol defines four time types: UTCTimestamp, UTCTimeOnly,
TZTimestamp, and TZTimeOnly.  Field values of these types can be added
using dedicated functions, avoiding the need to translate and format
time values in the application code.

.. code-block:: python

    message.append_timestamp(52, precision=6, header=True)  # UTCTimestamp
    message.append_timestamp(1132, utc=False)  # TZTimestamp
    message.append_time_only(1495, start_time)  # UTCTimeOnly
    message.append_time_only(1079, maturity_time, utc=False)  # TZTimeOnly

The first parameter to these functions is the field's tag number.  The
second parameter is optional: if None or not supplied, it defaults to the
current time, otherwise it must be a Unix epoch time (like from
``time.time()``), or a ``datetime`` instance.

There are three keyword parameters: ``precision`` which can be 0 for just
seconds, 3 for milliseconds or 6 for microseconds; ``utc`` which is
``True`` by default but can be set ``False`` for TZTimestamp and TZTimeOnly;
and ``header`` to insert this field in the header rather than the body.

Time fields can also be set using a string value if the application already
has the value in the correct format or prefers to manage the formatting
itself.

Repeating Groups
................

Data Fields
...........


Encoding
--------
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
"nth" value is an integer indicating the number of the group to use (note
that the first group is number one, not zero).
