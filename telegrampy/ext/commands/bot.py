"""
MIT License

Copyright (c) 2020-2024 ilovetocode

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

from __future__ import annotations

import importlib
import sys
import traceback
import types
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import telegrampy
from . import errors
from .cog import Cog
from .context import Context
from .core import Command
from .help import HelpCommand, DefaultHelpCommand

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Concatenate

    from telegrampy import Message

    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    ContextT = TypeVar("ContextT", bound="Context")
    CommandT = TypeVar("CommandT", bound="Command")
    CogT = TypeVar("CogT", bound="Cog")

    P = ParamSpec("P")

_default_help = DefaultHelpCommand()


class Bot(telegrampy.Client):
    r"""Represents a Telegram bot.

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
    \*\*options:
        Options to pass into :class:`telegrampy.Client`.

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

    def __init__(
        self,
        token: str, *,
        description: Optional[str] = None,
        owner_id: Optional[int] = None,
        owner_ids: Optional[List[int]] = None,
        help_command: Optional[HelpCommand] = _default_help,
        **options: Any
    ):
        super().__init__(token, **options)
        self.owner_id: Optional[int] = owner_id
        self.owner_ids: Optional[List[int]] = owner_ids
        self.description: Optional[str] = description

        self.commands_dict: Dict[str, Command] = {}
        self.cogs: Dict[str, Cog] = {}
        self.extensions: Dict[str, types.ModuleType] = {}

        self._help_command: Optional[HelpCommand] = None
        self.help_command = help_command

    @property
    def help_command(self) -> Optional[HelpCommand]:
        """Optional[:class:`telegrampy.ext.commands.HelpCommand`]: The bot's help command."""
        return self._help_command

    @help_command.setter
    def help_command(self, value: Optional[HelpCommand]) -> None:
        if value is not None:
            if not isinstance(value, HelpCommand):
                raise TypeError("The new help command must inherit from HelpCommand.")
            if self._help_command is not None:
                self._help_command._remove_from_bot(self)
            self._help_command = value
            value._add_to_bot(self)
        else:
            if self._help_command is not None:
                self._help_command._remove_from_bot(self)
            self._help_command = None

    @property
    def commands(self) -> List[Command]:
        """List[:class:`Command`] A list of the commands."""

        return list(self.commands_dict.values())

    def _get_all_command_names(self) -> List[str]:
        all_names = []
        for command in self.commands_dict.values():
            all_names.append(command.name)
            all_names.extend(command.aliases)

        return all_names

    def get_command(self, name: str) -> Optional[Command]:
        """Gets a command by name.

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

    async def get_context(self, message: Message, *, cls: Type[ContextT] = Context) -> Optional[ContextT]:
        """|coro|

        Gets context for a given message.

        Parameters
        ----------
        message: :class:`telegrampy.Message`
            The message to get context from.

        Returns
        -------
        Optional:class:`telegrampy.ext.commands.Context`]
            The context created, if applicable.

        Raises
        ------
        :class:`telegrampy.ext.commands.CommandNotFound`
            The command specified was not found.
        """

        if not hasattr(self, "_username"):
            me = await self.get_me()
            self._username = me.username

        if (
            message.content is not None
            and message.author is not None
            and not message.author.is_bot
            and message.entities[0].type == "bot_command"
            and message.entities[0].offset == 0
        ):
            parts = message.entities[0].value.split("@")

            if len(parts) == 1 or parts[1] == self._username:
                return cls(
                    bot=self,
                    message=message,
                    command=self.get_command(parts[0][1:]),
                    invoked_with=parts[0][1:],
                    chat=message.chat,
                    author=message.author,
                    args=[],
                    kwargs={}
                    )

    def load_extension(self, extension: str) -> None:
        """Loads an extension.

        Parameters
        ----------
        extension: :class:`str`
            The module location of the extension.

        Raises
        ------
        :exc:`telegrampy.ExtensionAlreadyLoaded`
            The extension is already loaded.
        :exc:`AttributeError`
            The extension has no setup function.
        """

        if extension in self.extensions:
            raise errors.ExtensionAlreadyLoaded(extension)

        # Attempt to import the extension
        try:
            lib = importlib.import_module(extension)
        except ModuleNotFoundError:
            raise errors.ExtensionNotFound(extension) from None
        except Exception as exc:
            raise errors.ExtensionFailed(extension, exc) from exc

        # Attempt to get setup function
        try:
            setup = getattr(lib, "setup")
        except AttributeError:
            self._cleanup_extension(lib)
            raise errors.NoEntryPointError(extension) from None

        # Attempt to setup extension
        try:
            setup(self)
        except Exception as exc:
            self._cleanup_extension(lib)
            raise errors.ExtensionFailed(extension, exc) from exc

        self.extensions[lib.__name__] = lib

    def unload_extension(self, extension: str) -> None:
        """Unloads an extension.

        Parameters
        ----------
        extension: :class:`str`
             The module location of the extension.
        """

        if extension not in self.extensions:
            raise errors.ExtensionNotLoaded(extension)

        lib = sys.modules[extension]

        self._cleanup_extension(lib)
        self.extensions.pop(extension)

    def reload_extension(self, extension: str) -> None:
        """Reloads an extension.

        Parameters
        ----------
        extension: :class:`str`
            The module location of the extension.
        """

        if extension not in self.extensions:
            raise errors.ExtensionNotLoaded(f"{extension} is not loaded")

        # Save the current state
        lib = sys.modules[extension]
        modules = {key: value for key, value in sys.modules.items() if key == extension or key.startswith(f"{extension}.")}

        # Remove the extension
        self.unload_extension(extension)

        try:
            # Attempt to load it back
            self.load_extension(extension)
        except Exception:
            # If this fails then revert the changes back
            self.extensions[lib.__name__] = lib
            lib.setup(self)
            sys.modules.update(modules)

            # Then re-raise the error
            raise

    def _cleanup_extension(self, extension: types.ModuleType) -> None:
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

    def add_cog(self, cog: Cog) -> None:
        """Adds a cog to the bot.

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

    def remove_cog(self, cog: str) -> None:
        """Removes and cog from the bot.

        Parameters
        ----------
        cog: :class:`str`
            The name of the cog to remove.
        """

        actual_cog = self.cogs.get(cog)
        if not actual_cog:
            return
        actual_cog._remove(self)
        self.cogs.pop(actual_cog.qualified_name)

    async def on_message(self, message):
        await self.process_commands(message)

    async def process_commands(self, message: Message) -> None:
        """|coro|

        Process commands that have been registered.
        By default this is called in on_message. If you override Bot.on_message you need to call this manually.

        Parameters
        ---------
        message: :class:`telegrampy.Message`
            The message to process.
        """

        ctx = await self.get_context(message)
        if ctx is not None:
            await self.invoke(ctx)

    async def invoke(self, ctx: Context) -> None:
        if not ctx.command:
            exc = errors.CommandNotFound(f"Command '{ctx.invoked_with}' is not found")
            return self.dispatch("command_error", ctx, exc)

        self.dispatch("command", ctx)
        try:
            await ctx.command.invoke(ctx)
        except Exception as exc:
            self.command_failed = True
            self.dispatch("command_error", ctx, exc)
        else:
            self.dispatch("command_completion", ctx)

    def command(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]],
            ]
        ], Command[CogT, P, T]]:
        r"""Turns a function into a command.

        Parameters
        ----------
        \*args:
            The arguments.
        \*\*kwargs:
            The keyword arguments.
        """

        def deco(
            func: Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]],
            ]
        ) -> Command[CogT, P, T]:
            name = kwargs.get("name") or func.__name__

            kwargs["name"] = name
            if name in self._get_all_command_names():
                raise errors.CommandRegistrationError(f"{name} is already registered as a command name or alias")

            command = Command(func, **kwargs)
            command.checks = getattr(func, "_command_checks", [])

            self.commands_dict[name] = command
            return command

        return deco

    def add_command(self, command: CommandT) -> CommandT:
        """Adds a command.

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
            raise errors.CommandRegistrationError(f"{command.name} is already registered as a command name or alias")

        self.commands_dict[command.name] = command
        return command

    def remove_command(self, name: str) -> Optional[Command]:
        """Removes a command by name.

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

    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        if self._listeners.get("on_command_error"):
            return

        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    async def sync(self):
        """|coro|
        
        Sets the user-facing Telegram commands to the curently registered commands with the instance.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Setting the currently registered comands failed. This will happen of commands are missing a description.
        """

        await self.http.set_my_commands([{
            "command": command.name,
            "description": command.description
        } for command in self.commands])
