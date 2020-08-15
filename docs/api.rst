.. currentmodule:: pygram

API Reference
=============

Client
---

.. autoclass:: Client
    :members:

Events
------

.. function:: on_message(message: pygram.Message)

    Called when a message is sent

.. function:: on_message_edit(message: pygram.Message)

    Called when a message is edited

.. function:: on_poll(poll: pygram.Poll)

    Called when poll is created or updated 


Message
-------

.. autoclass:: Message
    :members:

User
----

.. autoclass:: User
    :members:

Chat
----

.. autoclass:: Chat
    :members:

Files
-----

.. autoclass:: Document
    :members:
.. autoclass:: Photo
   :members:

Poll
----

.. autoclass:: Poll
    :members:

Errors
------

.. autoclass:: TelegramException
    :members:

.. autoclass:: CommandError
    :members:

.. autoclass:: CommandNotFound
    :members:

.. autoclass:: CommandRegistrationError
    :members:

.. autoclass:: ExtensionNotLoaded
    :members:

.. autoclass:: ExtensionAlreadyLoaded
    :members:

.. autoclass:: MissingRequiredArgument
    :members:

.. autoclass:: BadArgument
    :members:

.. autoclass:: CheckFailure
    :members:

.. autoclass:: NotOwner
    :members:

.. autoclass:: PrivateChatOnly
    :members:

.. autoclass:: GroupOnly
    :members:

.. autoclass:: HTTPException
    :members: