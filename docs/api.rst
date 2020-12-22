.. currentmodule:: telegrampy

API Reference
=============

Client
------

.. autoclass:: Client
    :members:

Events
~~~~~~

.. function:: on_message(message: telegrampy.Message)

    Called when a message is sent.

.. function:: on_message_edit(message: telegrampy.Message)

    Called when a message is edited.

.. function:: on_error(error)

    Called when an error occurs.

Utilities
---------

.. autofunction:: telegrampy.utils.escape_markdown


Telegram Models
---------------

Message
~~~~~~~

.. autoclass:: Message
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

.. autoclass:: InvalidToken
    :members:

.. autoclass:: Forbidden
    :members:

.. autoclass:: Conflict
    :members: