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

import types
import inspect

from .core import Command


class CogMeta(type):
    """Metaclass for Cog."""

    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        attrs["__cog_name__"] = kwargs.pop("name", name)

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        commands = []
        listeners = []

        for base in new_cls.__mro__:
            for command in base.__dict__.values():
                # Add the command if object is a command
                if isinstance(command, Command):
                    commands.append(command)

                # If object is a method and it has _cog_listener attribute, add the listener
                elif isinstance(command, types.FunctionType):
                    if hasattr(command, "_cog_listener"):
                        try:
                            listeners.append(command)
                        except AttributeError:
                            pass

        new_cls.commands = commands
        new_cls.listeners = listeners
        return new_cls


class Cog(metaclass=CogMeta):
    """
    Base cog class.

    Attributes
    ----------
    commands: List[:class:`telegrampy.Command`]
        The cog's commands.
    listeners: :class:`list`
        The cog's listeners.
    """

    @property
    def qualified_name(self):
        """:class:`str`: The cog's name."""
        return self.__cog_name__

    @property
    def description(self):
        """:class:`str`: The cog's description."""
        return inspect.getdoc(self)

    @classmethod
    def listener(cls, name: str = None):
        """
        Makes a method in a cog a listener.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the event to register the function as.
        """

        def deco(func):
            func._cog_listener = name or func.__name__
            return func

        return deco
    
    def _add(self, bot):
        for command in self.commands:
            command.bot = bot
            command.cog = self
            bot.add_command(command)
        for listener in self.listeners:
            bot.add_listener(getattr(self, listener.__name__), listener._cog_listener)

    def _remove(self, bot):
        for command in self.commands:
            bot.remove_command(command.name)
        for listener in self.listeners:
            bot.remove_listener(getattr(self, listener.__name__))

    def cog_check(self, ctx):
        return True
