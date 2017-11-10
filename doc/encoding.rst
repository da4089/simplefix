

Encoding
--------

Once all fields are set, calling ``encode()`` will return a byte buffer
containing the correctly formatted FIX message, with fields in the required
order, and automatically added and set values for the BodyLength (9) and
Checksum (10) fields.

.. code-block:: python

    byte_buffer = message.encode()


Raw Mode
........

Note that if you want to manually control the ordering of all fields, or
the value of the BodyLength (9) or Checksum (10) fields, there's a 'raw'
flag to the ``encode()`` method that disables the default automatic
functionality.

.. code-block:: python

    byte_buffer = message.encode(True)

This is primarily useful for creating known-bad messages for testing
purposes.


