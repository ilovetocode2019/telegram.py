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
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)

import telegrampy
from . import errors
from .cog import Cog
from .context import Context
from .core import Command, command
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

        self._extensions: Dict[str, types.ModuleType] = {}
        self._commands: Dict[str, Command] = {}
        self._cogs: Dict[str, Cog] = {}

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
        """List[:class:`Command`]: A list of the commands added to the bot."""
        return list(self._commands.values())

    @property
    def cogs(self) -> Mapping[str, Cog]:
        """Mapping[:class:`str`, :class:`.Cog`]: A read-only mapping of cogs added to the bot."""
        return types.MappingProxyType(self._cogs)

    @property
    def extensions(self) -> Mapping[str, types.ModuleType]:
        return types.MappingProxyType(self._extensions)

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

        for command in self._commands.values():
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
            and len(message.entities) > 0
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

    async def load_extension(self, name: str) -> None:
        """|coro|

        Loads an extension.

        Parameters
        ----------
        name: :class:`str`
            The module location of the extension.

        Raises
        ------
        ExtensionAlreadyLoaded
            The extension is already loaded.
        ExtensionNotFound
            The module to load as an extension could not be found.
        NoEntryPointError
            The extension has no ``setup`` function.
        ExtensionFailed
            Importing of the extension or execution of it's ``setup`` function failed.
        """

        if name in self._extensions:
            raise errors.ExtensionAlreadyLoaded(name)

        try:
            lib = importlib.import_module(name)
        except ModuleNotFoundError:
            raise errors.ExtensionNotFound(name) from None
        except Exception as exc:
            raise errors.ExtensionFailed(name, exc) from exc

        try:
            setup = getattr(lib, "setup")
        except AttributeError:
            await self._cleanup_extension(lib)
            raise errors.NoEntryPointError(name) from None

        try:
            await setup(self)
        except Exception as exc:
            await self._cleanup_extension(lib)
            raise errors.ExtensionFailed(name, exc) from exc

        self._extensions[lib.__name__] = lib

    async def unload_extension(self, name: str) -> None:
        """|coro|

        Unloads an extension.

        Parameters
        ----------
        name: :class:`str`
            The module location of the extension.

        Raises
        ------
        ExtensionNotLoaded
            The extension is not loaded.
        """

        lib = self._extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        await self._cleanup_extension(lib)

    async def reload_extension(self, name: str) -> None:
        """|coro|

        Unloads and loads back the extension, reverting to the original state if anything fails.

        Parameters
        ----------
        name: :class:`str`
            The module location of the extension.

        Raises
        ------
        ExtensionNotLoaded
            The extension is not loaded.
        ExtensionNotFound
            The module to load as an extension could not be found.
        NoEntryPointError
            The extension has no ``setup`` function.
        ExtensionFailed
            Importing of the extension or execution of it's ``setup`` function failed.
        """

        lib = self._extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        # save the current state to rollback
        modules = {key: value for key, value in sys.modules.items() if self._is_submodule(name, key)}
        await self._cleanup_extension(lib)
        del self._extensions[name]

        try:
            # attempt to load it back
            await self.load_extension(name)
        except Exception:
            # revert back to original state and re-raise exception
            self._extensions[lib.__name__] = lib
            await lib.setup(self)
            sys.modules.update(modules)
            raise

    async def _cleanup_extension(self, extension: types.ModuleType) -> None:
        for name, cog in self._cogs.copy().items():
            if self._is_submodule(extension.__name__, cog.__module__):
                await self.remove_cog(name)

        for name, command in self._commands.copy().items():
            if self._is_submodule(extension.__name__, command.__module__):
                self.remove_command(name)

        for name, listeners in self._listeners.copy().items():
            for listener in listeners:
                if self._is_submodule(extension.__name__, listener.__module__):
                    self.remove_listener(listener)

        try:
            await extension.teardown()
        except Exception:
            pass # ignore missing teardown functions or any failures inside of it

        for name in sys.modules.copy().keys():
            if self._is_submodule(extension.__name__, name):
                del sys.modules[name]

    def _is_submodule(self, parent: str, child: str) -> bool:
        return parent == child or child.startswith(f"{parent}.")

    async def add_cog(self, cog: Cog , *, override: bool = False) -> None:
        """|coro|

        Adds a cog to the bot.

        Parameters
        ----------
        cog: :class:`.Cog`
            The cog to add.
        override: :class:`bool`
            Whether to remove conflicting cogs with the same name, rather than raising an exception.

        Raises
        ------
        TypeError
            The cog is not a subclass of :class:`.Cog`.
        RuntimeError
            A cog with the same name is already added.
        CommandRegistrationError
            The cog has a command with the same name as one that is already registered.
        """

        if not isinstance(cog, Cog):
            raise TypeError("Cog is not a subclass of Cog")

        if cog.qualified_name in self._cogs:
            if override:
                await self.remove_cog(cog.qualified_name)
            else:
                raise RuntimeError(f"Cog with name '{cog.qualified_name}' is already added")

        await cog._add_to_bot(self)
        self._cogs[cog.qualified_name] = cog

    async def remove_cog(self, name: str) -> Optional[Cog]:
        """|coro|

        Removes a cog from the bot.

        Parameters
        ----------
        name: :class:`str`
            The name of the cog to remove.

        Returns
        -------
        Optional[:class:`.Cog`]
            The cog that was removed, if found.
        """

        cog = self._cogs.pop(name, None)
        if cog:
            await cog._remove_from_bot(self)
        return cog

    def get_cog(self, name: str) -> Optional[Cog]:
        """Returns the cog instance added to the bot by name, if found.

        Parameters
        ----------
        name: :class:`str`
            The name of the cog to look for.

        Returns
        --------
        Optional[:class:`.Cog`]
            The cog, if found.
        """

        return self._cogs.get(name)

    async def on_message(self, message):
        await self.process_commands(message)

    async def process_commands(self, message: Message) -> None:
        """|coro|

        Process commands that have been registered.
        By default this is called in on_message. If you override :meth:`.on_message` you need to call this manually.

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
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]],
            ]
        ], Command[CogT, P, T]]:
        r"""Turns a function into a :class:`.Command` and adds it to the bot.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the command to create, defaulting to the name of the function.
        \*\*kwargs
            The kwargs to pass into the :class:`.Command` constructor.

        Raises
        ------
        CommandRegistrationError
            The command name or one if its aliases is already registered by a different command.
        TypeError
            The function is not a coroutine.
        """

        def deco(
            func: Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]],
            ]
        ) -> Command[CogT, P, T]:
            ret = command(name, **kwargs)(func)
            self.add_command(ret)
            return ret

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

        all_names = []
        for name in self._commands:
            all_names.append(name)
            all_names.extend(self._commands[name].aliases)

        if command.name in all_names:
            raise errors.CommandRegistrationError(command.name)
        for alias in command.aliases:
            if alias in all_names:
                raise errors.CommandRegistrationError(alias, alias_conflict=True)

        self._commands[command.name] = command
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

        return self._commands.pop(name, None)

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
