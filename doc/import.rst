Importing
=========

You can import the *simplefix* module maintaining its internal structure,
or you can import some or all bindings directly.

.. code-block:: python
    :linenos:

    import simplefix

    fix_msg = simplefix.Message()


Or

.. code-block:: python
    :linenos:

    from simplefix import *

    fix_msg = Message()


Note that the "import *" form is explicitly supported, with the exposed
namespace explicitly managed to contain only the public features of the
package.

All the example code in this document will use the first form, which is
recommended.



