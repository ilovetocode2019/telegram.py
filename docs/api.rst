.. currentmodule:: pygram

API Reference
=============

Client
------

.. autoclass:: Client
    :members:

Events
------

.. function:: on_message(message: pygram.Message)

    Called when a message is sent.

.. function:: on_edit(before: pygram.Message, after: pygram.Message)

    Called when a message is edited.

.. function:: on_poll(poll: pygram.Poll)

    Called when poll is created or updated.

Utilities
---------

.. autofunction:: pygram.utils.escape_markdown


Telegram Models
---------------

Message
~~~~~~~

.. autoclass:: Message
    :members:

Context
~~~~~~~

.. autoclass:: Context
    :members:

User
~~~~

.. autoclass:: User
    :members:

Chat
~~~~

.. autoclass:: Chat
    :members:

Files
~~~~~

.. autoclass:: Document
    :members:
.. autoclass:: Photo
   :members:

Poll
~~~~

.. autoclass:: Poll
    :members:


Exceptions
----------

.. autoclass:: TelegramException
    :members:

.. autoclass:: HTTPException
    :members:
