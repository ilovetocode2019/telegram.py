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

import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Optional, TypeVar

from telegrampy import utils
from telegrampy.ext.commands.errors import CommandRegistrationError

from .core import Command

if TYPE_CHECKING:
    from .bot import Bot

    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    CoroFunc = Callable[..., Coro[Any]]
    FuncT = TypeVar("FuncT", bound=Callable[..., Any])


class CogMeta(type):
    """Metaclass for creating new :class:`.Cog` instances."""

    __cog_name__: str
    __cog_description__: str
    __cog_commands__: List[Command]
    __cog_listeners__: List[CoroFunc]

    def __new__(cls, name, bases, attrs, **kwargs):
        description = kwargs.pop("description", None)
        if description is None:
            description = inspect.cleandoc(attrs.get("__doc__", ""))

        attrs["__cog_name__"] = kwargs.pop("name", name)
        attrs["__cog_description__"] = description

        commands = {}
        listeners = {}
        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)

        for base in new_cls.__mro__:
            for name, value in base.__dict__.items():
                if name in commands or name in listeners:
                    continue
                elif isinstance(value, staticmethod):
                    value = value.__func__

                if isinstance(value, Command):
                    commands[name] = value
                elif hasattr(value, "__cog_listener__"):
                    listeners[name] = value

        new_cls.__cog_commands__ = list(commands.values())
        new_cls.__cog_listeners__ = list(listeners.values())
        return new_cls

    @property
    def qualified_name(cls) -> str:
        return cls.__cog_name__


class Cog(metaclass=CogMeta):
    """The base cog class that cogs inherit from."""

    __cog_name__: str
    __cog_description__: str
    __cog_commands__: List[Command]
    __cog_listeners__: List[CoroFunc]

    @property
    def qualified_name(self) -> str:
        """:class:`str`: The cog's name."""
        return self.__cog_name__

    @property
    def description(self) -> Optional[str]:
        """:class:`str`: The cog's description."""
        return self.__cog_description__

    @classmethod
    def listener(cls, name: Optional[str] = None) -> Callable[[CoroFunc], CoroFunc]:
        """Makes a method in a cog a listener.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the event to register the function as.
        """

        def deco(func: FuncT) -> FuncT:
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Listener callback is not a coroutine.")

            func.__cog_listener__ = True
            func.__cog_listener_names__ = getattr(func, "__cog_listener_names__", []) + [name or func.__name__]
            return func

        return deco

    async def _add_to_bot(self, bot: Bot) -> None:
        await utils.maybe_await(self.cog_load)

        for index, command in enumerate(self.__cog_commands__):
            command.cog = self
            try:
                bot.add_command(command)
            except CommandRegistrationError as exc:
                for added_command in self.__cog_commands__[:index]:
                    bot.remove_command(added_command.name)
                raise exc

        for listener in self.__cog_listeners__:
            method = listener.__get__(self)
            for event_name in listener.__cog_listener_names__:
                bot.add_listener(method, event_name)

    async def _remove_from_bot(self, bot: Bot) -> None:
        for command in self.__cog_commands__:
            bot.remove_command(command.name)
        for listener in self.__cog_listeners__:
            bot.remove_listener(listener)

        try:
            await utils.maybe_await(self.cog_unload)
        except Exception:
            pass

    def cog_check(self, ctx):
        return True

    async def cog_load(self):
        """|maybecoro|

        Called when the cog is added to the bot.
        Subclasses can override this with their own behavior.
        """

        pass

    async def cog_unload(self):
        """|maybecoro|

        Called when the cog is removed from the bot.
        Subclasses can override this with their own behavior.
        """

        pass
