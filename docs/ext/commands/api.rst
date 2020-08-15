.. currentmodule:: pygram

.. _ext_commands_api:

API Reference
=============

Bot
---

.. autoclass:: pygram.ext.commands.Bot
    :members:
    :inherited-members:

Commands
--------

.. autofunction: pygram.ext.commands.command

.. autofunction: pygram.ext.commands.group

.. autoclass:: pygram.ext.commands.Command
    :members:

.. autoclass:: pygram.ext.commands.Cog
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

Context
-------

.. autoclass:: pygram.ext.commands.Context
    :members:

Errors
------

.. autoclass:: pygram.ext.commands.CommandError
    :members:

.. autoclass:: pygram.ext.commands.CommandNotFound
    :members:

.. autoclass:: pygram.ext.commands.CommandRegistrationError
    :members:

.. autoclass:: pygram.ext.commands.ExtensionNotLoaded
    :members:

.. autoclass:: pygram.ext.commands.ExtensionAlreadyLoaded
    :members:

.. autoclass:: pygram.ext.commands.MissingRequiredArgument
    :members:

.. autoclass:: pygram.ext.commands.BadArgument
    :members:

.. autoclass:: pygram.ext.commands.CheckFailure
    :members:

.. autoclass:: pygram.ext.commands.NotOwner
    :members:

.. autoclass:: pygram.ext.commands.PrivateChatOnly
    :members:

.. autoclass:: pygram.ext.commands.GroupOnly
    :members:
