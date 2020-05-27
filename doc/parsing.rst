Parsing Messages
----------------

To parse a FIX message, first create an instance of the FixParser class.

.. code-block:: python

    parser = simplefix.FixParser()

To extract FIX messages from a byte buffer, such as that received from a
socket, you should append it to the internal reassembly buffer using
``append_buffer()`` .  At any time, you can call ``get_message()`` : if there's
no complete message in the parser's internal buffer, it'll return None,
otherwise, it'll return a ``FixMessage`` instance.

.. code-block:: python

    fix_buffer = parser.append_buffer()
    message = fix_buffer.get_message()


Once you've received a ``FixMessage`` from ``get_message()`` , you can: check
the number of fields with ``count()`` , retrieve the value of a field using
``get()`` or the built-in "[ ]" syntax, or iterate over all the fields using
"for ... in ...".

.. code-block:: python

    message.count(49)
    >>> 1

    message.get(35)
    >>> 'A'

    message["35"]
    >>> 'A'

Members of repeating groups can be accessed using ``get(tag, nth)``, where the
"nth" value is an integer indicating the number of the group to use (note
that the first group is number one, not zero).

.. code-block:: python

    messsage = get(9061, 2)
    >>> 22 
