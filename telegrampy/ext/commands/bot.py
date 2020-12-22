"""
MIT License

Copyright (c) 2020 ilovetocode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import traceback
import types
import importlib
import sys

import telegrampy
from .core import Command
from .cog import Cog
from .context import Context
from .errors import *
from .help import HelpCommand, DefaultHelpCommand


_default_help = DefaultHelpCommand()

class Bot(telegrampy.Client):
    """
    Represents a Telegram bot.

    Parameters
    ----------
    token: :class:`str`
        The API token.
    description: Optional[:class:`str`]
        The bot's description.
    owner_id: Optional[:class:`int`]
        The owner's ID.
    owner_ids: Optional[List[:class:`int`]]
        The owner IDs.
    help_command: Optional[:class:`telegrampy.ext.commands.HelpCommand`]
        The bot's help command.
        Defaults to :class:`telegrampy.ext.commands.DefaultHelpCommand`

    Attributes
    ----------
    description: Optional[:class:`str`]
        The bot's description.
    owner_id: Optional[:class:`int`]
        The owner's ID.
    owner_ids: Optional[List[:class:`int`]]
        The owner IDs.
    cogs: Mapping[:class:`str`, :class:`telegrampy.ext.commands.Cog`]
        A dictonary of cogs that are loaded.
    extensions: Mapping[:class:`str`, :class:`types.ModuleType`]
        A dictonary of extensions that are loaded.
    """

    def __init__(self, token: str,  *, description: str = None, owner_id: int = None, owner_ids: list = None, help_command: HelpCommand = _default_help):
        super().__init__(token)
        self.owner_id = owner_id
        self.owner_ids = owner_ids
        self.description = description

        self.commands_dict = {}

        self.cogs = {}
        self.extensions = {}

        if help_command:
            self.help_command = help_command

    @property
    def help_command(self):
        """:class:`telegrampy.ext.commands.HelpCommand`:
            The bot's help command.
        """
        return self._help_command

    @help_command.setter
    def help_command(self, value: HelpCommand):
        if not isinstance(value, HelpCommand):
            raise TypeError("The new help command must inherit from HelpCommand.")

        value._add_to_bot(self)
        self._help_command = value

    @property
    def commands(self):
        """
        :class:`list`:
            A list of the commands.
        """

        return list(self.commands_dict.values())

    def _get_all_command_names(self):
        all_names = []
        for command in self.commands_dict.values():
            all_names.append(command.name)
            all_names.extend(command.aliases)

        return all_names

    def get_command(self, name: str):
        """
        Gets a command by name.

        Parameters
        ----------
        name: :class:`str`
            The command name.

        Returns
        --------
        :class:`telegrampy.ext.commands.Command`
            The command with the name.
        """

        for command in self.commands_dict.values():
            if name in command.aliases or command.name == name:
                return command

    async def get_context(self, message: telegrampy.Message):
        """
        Gets context for a given message.

        Parameters
        ----------
        message: :class:`telegrampy.Message`
            The message to get context from.

        Returns
        -------
        :class:`telegrampy.ext.commands.Context`
            The context created.

        Raises
        ------
        :class:`telegrampy.ext.commands.CommandNotFound`
            The command specified was not found.
        """

        content = message.content.split(" ")[0]
        command = None
        if content.startswith("/"):
            splited = content.split("@")
            if len(splited) == 1 or (len(splited) != 1 and splited[1] == (await self.user()).username):
                command_name = splited[0][1:]
                command = self.get_command(command_name)
                if not command:
                    raise CommandNotFound(command_name)

        kwargs = {"command": command}
        kwargs["args"] = []
        kwargs["kwargs"] = {}
        kwargs["message"] = message
        kwargs["chat"] = message.chat
        kwargs["author"] = message.author
        kwargs["bot"] = self
        return Context(**kwargs)

    def load_extension(self, extension: str):
        """
        Loads an extension.

        Parameters
        ----------
        location: :class:`str`
            The location of the extension.

        Raises
        ------
        :exc:`telegrampy.ExtensionAlreadyLoaded`
            The extension is already loaded.
        :exc:`AttributeError`
            The extension has no setup function.
        """

        if extension in self.extensions:
            raise ExtensionAlreadyLoaded(extension)

        lib = importlib.import_module(extension)
        self.extensions[lib.__name__] = lib

        if not hasattr(lib, "setup"):
            raise AttributeError("Extension has no setup function")

        lib.setup(self)

    def unload_extension(self, extension: str):
        """
        Unloads an extension.

        Parameters
        ----------
        location: :class:`str`
             The location of the extension.
        """

        if extension not in self.extensions:
            raise ExtensionNotLoaded(extension)

        lib = sys.modules[extension]

        self._cleanup_extension(lib)
        self.extensions.pop(extension)

    def reload_extension(self, extension: str):
        """
        Reloads an extension.

        Parameters
        ----------
        location: :class:`str`
            The location of the extension.
        """

        if extension not in self.extensions:
            raise ExtensionNotLoaded(f"{extension} is not loaded")

        # Save the current state
        lib = sys.modules[extension]
        modules = {key: value for key, value in sys.modules.items() if key == extension or key.startswith(f"{extension}.")}

        # Remove the extension
        self.unload_extension(extension)

        try:
            # Attempt to load it back
            self.load_extension(extension)
        except Exception as exc:
            # If this fails then revert the changes back
            self.extensions[lib.__name__] = lib
            lib.setup(self)
            sys.modules.update(modules)

            # Then re-raise the error
            raise

    def _cleanup_extension(self, extension):
        # Remove cogs, commands, and listeners from the bot
        for name, cog in self.cogs.copy().items():
            if cog.__module__ and (cog.__module__ == extension.__name__ or cog.__module__.startswith(f"{extension.__name__}.")):
                self.remove_cog(name)

        for name, command in self.commands_dict.copy().items():
            if command.__module__ and (command.__module__ == extension.__name__ or command.__module__.startswith(f"{extension.__name__}.")):
                self.remove_command(name)

        for name, listeners in self._listeners.copy().items():
            for listener in listeners:
                if listener.__module__ and (listener.__module__ == extension.__name__ or listener.__module__.startswith(f"{extension.__name__}.")):
                    self.remove_listener(listener)

        # Remove the module and any submodules
        for name in sys.modules.copy().keys():
            if name == extension.__name__ or name.startswith(f"{extension.__name__}."):
                sys.modules.pop(name, None)

    def add_cog(self, cog: Cog):
        """
        Adds a cog to the bot.

        Parameters
        ----------
        cog: :class:`telegrampy.ext.commands.Cog`
            The cog to add.

        Raises
        ------
        :exc:`TypeError`
            The cog is not a subclass of :class:`telegrampy.ext.commands.Cog` or the cog check is not a method.
        """

        if not isinstance(cog, Cog):
            raise TypeError("Cog is not a subclass of Cog")

        # Add the cog
        cog._add(self)
        self.cogs[cog.qualified_name] = cog

    def remove_cog(self, cog: str):
        """
        Removes and cog from the bot.

        Parameters
        ----------
        cog: :class:`str`
            The name of the cog to remove.
        """

        cog = self.cogs.get(cog)
        if not cog:
            return
        cog._remove(self)
        self.cogs.pop(cog.qualified_name)

    async def _use_command(self, ctx):
        await self._dispatch("command", ctx)

        try:
            await ctx.command.invoke(ctx)
        except Exception as exc:
            ctx.command_failed = True
            await self._dispatch("command_error", ctx, exc)

        if not ctx.command_failed:
            await self._dispatch("command_completion", ctx)

    async def _dispatch(self, event, *args):
        await super()._dispatch(event, *args)

        # If event is on_message, check if the message if a command
        # If it is a command, invoke the command
        if event == "message":
            message = args[0]
            if not message.content:
                return

            ctx = await self.get_context(message)

            if not ctx.command:
                return

            self.loop.create_task(self._use_command(ctx))

    def command(self, *args, **kwargs):
        """
        Turns a function into a command.

        Parameters
        ----------
        \*args:
            The arguments.
        \*\*kwargs:
            The keyword arguments.
        """

        def deco(func):
            name = kwargs.get("name") or func.__name__

            kwargs["name"] = name
            if name in self._get_all_command_names():
                raise CommandRegistrationError(f"{name} is already regeistered as a command name or alias")

            command = Command(func, **kwargs)
            command.checks = getattr(func, "_command_checks", [])

            self.commands_dict[name] = command
            return command

        return deco

    def add_command(self, command):
        """
        Adds a command.

        Parameters
        ----------
        command: :class:`telegrampy.ext.commands.Command`
            The command to add.

        Returns
        -------
        :class:`telegrampy.ext.commands.Command`
            The command added.

        Raises
        ------
        :exc:`telegrampy.ext.commands.CommandRegistrationError`
            The command name or one if its aliases is already registered by a different command.
        :exc:`TypeError`
            The command is not an instance of :class:`telegrampy.ext.commands.Command`.
        """

        if not isinstance(command, Command):
            raise TypeError("Command must be a subclass of Command")

        if command.name in self._get_all_command_names():
            raise CommandRegistrationError(f"{name} is already regeistered as a command name or alias")

        self.commands_dict[command.name] = command
        return command

    def remove_command(self, name: str):
        """
        Removes a command by name.

        Parameters
        ----------
        name: :class:`str`
            The name of the command to remove.

        Returns
        -------
        :class:`telegrampy.ext.commands.Command`:
            The command removed.
        """

        command = self.get_command(name)

        if not command:
            return

        self.commands_dict.pop(name)

        return command

    async def on_command_error(self, ctx, error):
        """The default command error handler."""

        if self._listeners.get("on_command_error"):
            return

        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )
