.. currentmodule:: telegrampy

.. _ext_commands_api:

API Reference
=============

Bot
---

.. autoclass:: telegrampy.ext.commands.Bot
    :members:
    :inherited-members:

Events
------

.. function:: on_command(ctx)

    Called when a command is invoked.

.. function:: on_command_completion(ctx)

    Called when a command is completed.

.. function:: on_command_error(ctx, error)

    Called when an error occurs in a command.

Command
-------

.. autofunction:: telegrampy.ext.commands.command

.. autoclass:: telegrampy.ext.commands.Command
    :members:

Checks
------

.. autofunction:: telegrampy.ext.commands.check

.. autofunction:: telegrampy.ext.commands.telegrampy.ext.commands.is_owner

.. autofunction:: telegrampy.ext.commands.is_private_chat

.. autofunction:: telegrampy.ext.commands.is_not_private_chat

Help Command
------------

.. autoclass:: telegrampy.ext.commands.HelpCommand
    :members:

.. autoclass:: telegrampy.ext.commands.DefaultHelpCommand
    :members:

Cog
---

.. autoclass:: telegrampy.ext.commands.Cog
    :members:

Context
-------

.. autoclass:: telegrampy.ext.commands.Context
    :members:

Converters
----------
..autoclass:: telegrampy.ext.commands.Converters
    :members:

.. autoclass:: telegrampy.ext.commands.UserConverter
    :members:

.. autoclass:: telegrampy.ext.commands.ChatConverter
    :members:

Exceptions
----------

.. autoclass:: telegrampy.ext.commands.CommandError
    :members:

.. autoclass:: telegrampy.ext.commands.CommandNotFound
    :members:

.. autoclass:: telegrampy.ext.commands.CommandRegistrationError
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionNotLoaded
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionAlreadyLoaded
    :members:

.. autoclass:: telegrampy.ext.commands.MissingRequiredArgument
    :members:

.. autoclass:: telegrampy.ext.commands.BadArgument
    :members:

.. autoclass:: telegrampy.ext.commands.CheckFailure
    :members:

.. autoclass:: telegrampy.ext.commands.NotOwner
    :members:

.. autoclass:: telegrampy.ext.commands.CommandInvokeError
    :members:

.. autoclass:: telegrampy.ext.commands.PrivateChatOnly
    :members:

.. autoclass:: telegrampy.ext.commands.GroupOnly
    :members:
