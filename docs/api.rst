.. currentmodule:: pygram

API Reference
=============

Bot
---

.. autoclass:: Bot
    :members:

Events
------

.. function:: on_message(message: pygram.Message)

    Called when a message is sent

.. function:: on_edit(before: pygram.Message, after: pygram.Message)

    Called when a message is edited

.. function:: on_poll(poll: pygram.Poll)

    Called when poll is created or updated 


Message
-------

.. autoclass:: Message
    :members:

Context
-------

.. autoclass:: Context
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

Commands
--------

.. autoclass:: Command
    :members:

.. autoclass:: Cog
    :members:

Checks
------
.. function:: check(check_function)

    Turns a function into a check

.. function:: is_owner()

    A command check for checking that the user is the owner

.. function:: is_private_chat()

    A command check for checking that the chat is a private chat

.. function:: is_not_private_chat()

    A command check for checking that the chat is not a private chat