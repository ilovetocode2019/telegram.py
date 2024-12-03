.. currentmodule:: telegrampy

.. _ext_commands_api:

API Reference
=============

Bot
---

.. autoclass:: telegrampy.ext.commands.Bot
    :members:
    :inherited-members:

    .. autofunction:: telegrampy.ext.commands.Bot.command
        :decorator:

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
    :decorator:

.. autofunction:: telegrampy.ext.commands.is_owner
    :decorator:

.. autofunction:: telegrampy.ext.commands.is_private_chat
    :decorator:

.. autofunction:: telegrampy.ext.commands.is_not_private_chat
    :decorator:

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

.. autoclass:: telegrampy.ext.commands.Context()
    :members:

Converters
----------

.. autoclass:: telegrampy.ext.commands.Converter
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

.. autoclass:: telegrampy.ext.commands.ExtensionError
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionAlreadyLoaded
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionNotLoaded
    :members:

.. autoclass:: telegrampy.ext.commands.NoEntryPointError
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionNotFound
    :members:

.. autoclass:: telegrampy.ext.commands.ExtensionFailed
    :members:

.. autoclass:: telegrampy.ext.commands.UserInputError
    :members:

.. autoclass:: telegrampy.ext.commands.MissingRequiredArgument
    :members:

.. autoclass:: telegrampy.ext.commands.BadArgument
    :members:

.. autoclass:: telegrampy.ext.commands.ArgumentParsingError
    :members:

.. autoclass:: telegrampy.ext.commands.ExpectedClosingQuote
    :members:

.. autoclass:: telegrampy.ext.commands.CheckFailure
    :members:

.. autoclass:: telegrampy.ext.commands.NotOwner
    :members:

.. autoclass:: telegrampy.ext.commands.PrivateChatOnly
    :members:

.. autoclass:: telegrampy.ext.commands.GroupOnly
    :members:

.. autoclass:: telegrampy.ext.commands.CommandInvokeError
    :members:
