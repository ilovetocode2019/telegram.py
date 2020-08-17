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

import pygram
from pygram import User, Chat

from .errors import *
from .context import Context


class Command:
    """
    Represents a command.

    Attributes
    ----------
    name: :class:`str`
        The name of the command.
    description: :class:`str`
        The description of the command.
    usage: :class:`str`
        The usage of the command.
    aliases: :class:`str`
        The aliases for the command.
    callback:
        The callback of the command.
    hidden: :class:`bool`
        If the command is hidden.
    cog: :class:`pygram.Cog`
        The cog the command is in.
    bot: :class:`pygram.Bot`
        The bot the command is in.
    """

    def __init__(self, func, **kwargs):
        self.callback = func

        self._data = kwargs
        self.name = kwargs.get("name") or func.__name__
        self.description = kwargs.get("description")
        self.usage = kwargs.get("usage")
        self.aliases = kwargs.get("aliases") or []
        self.hidden = kwargs.get("hidden") or False
        self.cog = None
        self.bot = None
        self.checks = []

    def __str__(self):
        return self.name

    def add_check(self, func):
        """
        Adds a check.

        Parameters
        ----------
        func:
            The function to add to the checks.
        """

        self.checks.append(func)

    def remove_check(self, func):
        """
        Removes a check.

        Parameters
        ----------
        func:
           The function to remove from the checks.
        """

        if func not in self.checks:
            return

        self.checks.remove(func)

    async def _convert_arg(self, ctx, converter, arg):
        try:
            if converter == User:
                return ctx.chat.get_member(arg)
            elif converter == Chat:
                return ctx.bot.get_chat(arg)
            else:
                return converter(arg)
        except:
            return None

    async def _parse_args(self, ctx: Context):
        given_args = ctx.message.content.split(" ")
        given_args.pop(0)

        if ctx.command:
            takes_args = [x[1] for x in list(inspect.signature(ctx.command.callback).parameters.items())]
            if ctx.command.cog:
                takes_args.pop(0)
            takes_args.pop(0)

            # Iter through the arguments
            for counter, argument in enumerate(takes_args):
                try:
                    # If argument can be positional, give one arg
                    if argument.kind in (inspect._ParameterKind.POSITIONAL_OR_KEYWORD, inspect._ParameterKind.POSITIONAL_ONLY):
                        give = given_args[0]
                        converter = argument.annotation
                        # If the argument as a converter, try and convert
                        if converter != inspect._empty:
                            give = await self._convert_arg(ctx, converter, give)
                            if not give:
                                raise BadArgument(give, converter.__name__)
                        ctx.args.append(give)
                        given_args.pop(0)

                    # If argument is a keyword argument, give the rest of the arguments
                    elif argument.kind == inspect._ParameterKind.KEYWORD_ONLY:
                        give = " ".join(given_args)
                        if give == "":
                            raise IndexError()

                        converter = argument.annotation
                        # If the argument has a converter, try and convert
                        if converter != inspect._empty:
                            give = await self._convert_arg(ctx, converter, give)
                            if not give:
                                raise BadArgument(give, converter.__name__)
                        ctx.kwargs[argument.name] = give

                    elif argument.kind == inspect._ParameterKind.VAR_POSITIONAL:
                        if len(given_args) == 0:
                            raise IndexError()
                        for give in given_args:
                            converter = argument.annotation
                            if converter != inspect._empty:
                                give = await self._convert_arg(ctx, converter, give)
                                if not give:
                                    raise BadArgument(give, converter.__name__)
                            ctx.args.append(give)

                except IndexError:
                    # If no argument does not have a default, raise MissingRequiredArgument
                    if argument.default == inspect._empty:
                        raise MissingRequiredArgument(argument.name)
                    # Otherwise set the argument to the default
                    if argument.kind in (inspect._ParameterKind.POSITIONAL_OR_KEYWORD, inspect._ParameterKind.POSITIONAL_ONLY):
                        ctx.args.append(argument.default)

    async def invoke(self, ctx: Context):
        """
        Invokes the command with given context.

        Parameters
        ----------
        ctx: :class:`pygram.Context`
            The context to invoke the command with.
        """

        # Checks
        for check in self.checks:
            if not check(ctx):
                raise CheckFailure("A check for this command has failed")

        if self.cog:
            if not self.cog.cog_check(ctx):
                raise CheckFailure("A check for this command has failed")

        other_args = []
        if self.cog:
            other_args.append(self.cog)
        other_args.append(ctx)

        await self._parse_args(ctx)

        return await self.callback(*other_args, *ctx.args, **ctx.kwargs)


def command(*args, **kwargs):
    """Turns a function into a command.

    See :class:`pygram.ext.commands.Command`
    for parameters.
    """

    def deco(func):
        kwargs["name"] = kwargs.get("name")

        command = Command(func, **kwargs)
        command.checks = getattr(func, "_command_checks", [])

        command = Command(func, **kwargs)
        return command

    return deco


def check(check_function):
    """Makes a check for a command."""

    def deco(func):
        if isinstance(func, Command):
            func.add_check(check_function)
        else:
            if not getattr(func, "_command_checks", None):
                func._command_checks = [check_function]
            else:
                func._command_checks.append(check_function)
        return func

        return

    return deco


def is_owner():
    """A command check for checking that the user is the owner."""

    def is_owner_check(ctx):
        if ctx.author.id not in (ctx.bot.owner_ids or [ctx.bot.owner_id]):
            raise NotOwner("You must be the owner to use this command")
        return True

    return check(is_owner_check)


def is_private_chat():
    """A command check for checking that the chat is a private chat."""

    def is_private_chat_check(ctx):
        if ctx.chat.type != "private":
            raise PrivateChatOnly()
        return True

    return check(is_private_chat_check)


def is_not_private_chat():
    """A command check for checking that the chat is not a private chat."""

    def is_not_private_chat_check(ctx):
        if ctx.chat.type == "private":
            raise GroupOnly()
        return True

    return check(is_not_private_chat_check)
