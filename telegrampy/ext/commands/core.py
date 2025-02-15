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
import sys
import types
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, Concatenate, ForwardRef, Generic, Literal, ParamSpec, TypeVar, Union, get_origin

from .context import Context
from .errors import *
from .converter import Converter, MAPPING as CONVERTERS_MAPPING
from .reader import ArgumentReader

if TYPE_CHECKING:
    from .bot import Bot
    from .cog import Cog

    ContextT = TypeVar("ContextT", bound="Context")
    CommandT = TypeVar("CommandT", bound="Command")

T = TypeVar("T")
Coro = Coroutine[Any, Any, T]
CoroFunc = Callable[..., Coro[Any]]
MaybeCoro = T | Coro
Check = Callable[[Context[Any]], MaybeCoro[bool]]

CogT = TypeVar("CogT", bound="Cog")
P = ParamSpec("P")


class Command(Generic[CogT, P, T]):
    """Represents a command.

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
    cog: :class:`telegrampy.ext.commands.Cog`
        The cog the command is in.
    bot: :class:`telegrampy.ext.commands.Bot`
        The bot the command is in.
    """

    def __init__(
        self,
        func: Callable[Concatenate[CogT, ContextT, P], Coro[T]] | Callable[Concatenate[ContextT, P], Coro[T]],
        **kwargs
    ) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Command callback is not a coroutine.")

        self.callback = func
        self.name: str = kwargs.get("name") or func.__name__
        self.description: str | None = kwargs.get("description")
        self.usage: str | None = kwargs.get("usage")
        self.aliases: list[str] = kwargs.get("aliases") or []
        self.hidden: bool = kwargs.get("hidden") or False
        self.cog: Cog | None = None
        self.bot: Bot | None = None
        self.checks: list[Check] = kwargs.get("checks") or []
        self.params: dict[str, inspect.Parameter] = get_parameters(func)

        try:
            self.checks: list[Check] = func.__command_checks__
        except AttributeError:
            self.checks: list[Check] = kwargs.get("checks", [])

    def __str__(self) -> str:
        return self.name

    @property
    def signature(self) -> str:
        """:class:`str`: Returns a signature for a command that can be used in help commands.

        <required> required param
        [optional] optional param
        [params...] optional list of params
        [optional=0] optional param defaults to 0
        """

        if self.usage:
            return self.usage

        final = []

        for name, param in self.params.items():
            if param.default is not param.empty:
                if param.default is None or (isinstance(param.default, str) and not param.default):
                    final.append(f"[{name}]")
                else:
                    final.append(f"[{name}={param.default}]")
            elif param.kind == param.VAR_POSITIONAL:
                final.append(f"[{name}...]")
            else:
                final.append(f"<{name}>")

        return " ".join(final)

    def add_check(self, func: Check) -> None:
        """Adds a check to the command.

        Parameters
        ----------
        func:
            The function to add to the checks.
        """

        self.checks.append(func)

    def remove_check(self, func: Check) -> None:
        """Removes a check from the command.

        Parameters
        ----------
        func:
           The function to remove from the checks.
        """

        if func not in self.checks:
            return

        self.checks.remove(func)

    async def _convert_argument(self, ctx: Context, argument: str, param: inspect.Parameter, converter: Any) -> Any:
        converter = CONVERTERS_MAPPING.get(converter, converter)
 
        if issubclass(converter, Converter):
            converter = converter()
        if isinstance(converter, Converter):
            try:
                return await converter.convert(ctx, argument)
            except CommandError:
                raise
            except Exception as exc:
                raise ConversionError(converter, exc) from exc
        else:
            try:
                return converter(argument)
            except CommandError:
                raise
            except Exception as exc:
                name = getattr(converter, "__name__", converter.__class__.__name__)
                raise BadArgument(f"Converting to '{name}' failed for parameter '{param.name}'") from exc

    async def _parse_argument(self, ctx: Context, argument: str | None, param: inspect.Parameter) -> Any:
        name = getattr(param.annotation, "name", param.annotation.__class__.__name__)
        origin = get_origin(param.annotation)

        if not argument:
            if param.default != param.empty:
                return param.default
            elif origin in [Union, types.UnionType] and type(None) in param.annotation.__args__:
                return None
            raise MissingRequiredArgument(param)
        elif param.annotation == param.empty:
            return argument

        if origin in [Union, types.UnionType]:
            for annotation in param.annotation.__args__:
                if annotation is type(None):
                    continue
                try:
                    return await self._convert_argument(ctx, argument, param, annotation)
                except CommandError:
                    pass
 
            if type(None) in param.annotation.__args__:
                return None

            raise BadArgument(f"Converting to '{name}' failed for parameter '{param.name}'")
        else:
            return await self._convert_argument(ctx, argument, param, param.annotation)

    async def _parse_arguments(self, ctx: Context) -> None:
        if not ctx.message.content:
            raise RuntimeError

        parser = ArgumentReader(ctx.message.content.split(" ", 1)[1] if " " in ctx.message.content else "")
        ctx.args = [ctx] if not self.cog else [self.cog, ctx]
        ctx.kwargs = {}

        for name, param in self.params.items():
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                result = await self._parse_argument(ctx, parser.argument(), param)
                ctx.args.append(result)
            elif param.kind == param.KEYWORD_ONLY:
                result = await self._parse_argument(ctx, parser.keyword_argument(), param)
                ctx.kwargs[name] = result
            elif param.kind == param.VAR_POSITIONAL:
                arguments = parser.extras()
                ctx.args.extend([await self._parse_argument(ctx, argument, param) for argument in arguments])

    async def can_run(self, ctx: Context) -> bool:
        """|coro|

        Checks if the command can run.

        Parameters
        ----------
        ctx: :class:`telegrampy.ext.commands.Context`
            The context invoking the command.

        Returns
        -------
        :class:`bool`
            A boolean indicating if the command can be invoked or not.

        Raises
        ------
        :exc:`telegrampy.ext.commands.CheckFailure`
            A check failed.
        """

        for check in self.checks:
            if not check(ctx):
                return False

        if self.cog and not self.cog.cog_check(ctx):
            return False

        return True

    async def invoke(self, ctx: Context) -> None:
        """|coro|

        Invokes the command with given context.

        Parameters
        ----------
        ctx: :class:`telegrampy.ext.commands.Context`
            The context invoking the command.

        Returns
        -------
        :class:`bool`
            A boolean that indicates if the command can be invoked or not.

        Raises
        ------
        :exc:`telegrampy.ext.commands.CommandError`
            The command failed.
        """

        if not await self.can_run(ctx):
            raise CheckFailure("The checks for this command failed")

        await self._parse_arguments(ctx)

        try:
            return await self.callback(*ctx.args, **ctx.kwargs)  # type: ignore
        except Exception as exc:
            ctx.command_failed = True
            raise CommandInvokeError(exc) from exc

def command(
    name: str | None = None,
    **kwargs: Any,
) -> Callable[
        [Callable[Concatenate[CogT, ContextT, P], Coro[T]] | Callable[Concatenate[ContextT, P], Coro[T]]],
        Command[CogT, P, T]
    ]:
    """Turns a function into a :class:`.Command`.

    Parameters
    ----------
    name: :class:`str` | None
        The name of the command to create, defaulting to the name of the function.
    kwargs:
        The keyword arguments to pass into the :class:`.Command` constructor.

    Raises
    ------
    TypeError
        The function is not a coroutine.
    """

    def deco(
        func: Callable[Concatenate[CogT, ContextT, P], Coro[T]] | Callable[Concatenate[ContextT, P], Coro[T]]
    ) -> Command[CogT, P, T]:
        return Command(func, name=name, **kwargs)

    return deco


def check(check_func: Check) -> Callable[[Command | CoroFunc], Command | CoroFunc]:
    """Makes a check for a command."""

    def deco(func: Command | CoroFunc) -> Command | CoroFunc:
        if isinstance(func, Command):
            func.add_check(check_func)
        else:
            if not hasattr(func, "__command_checks__"):
                func.__command_checks__ = [check_func]
            else:
                func.__command_checks__.append(check_func)

        return func

    return deco


def is_owner() -> Callable[[Command | CoroFunc], Command | CoroFunc]:
    """A command check for checking that the user is the owner."""

    def is_owner_check(ctx: Context) -> bool:
        if ctx.author.id not in (ctx.bot.owner_ids or [ctx.bot.owner_id]):
            raise NotOwner("You must be the owner to use this command")
        return True

    return check(is_owner_check)


def is_private_chat() -> Callable[[Command | CoroFunc], Command | CoroFunc]:
    """A command check for checking that the chat is a private chat."""

    def is_private_chat_check(ctx: Context) -> bool:
        if ctx.chat.type != "private":
            raise PrivateChatOnly()
        return True

    return check(is_private_chat_check)


def is_not_private_chat() -> Callable[[Command | CoroFunc], Command | CoroFunc]:
    """A command check for checking that the chat is not a private chat."""

    def is_not_private_chat_check(ctx: Context) -> bool:
        if ctx.chat.type == "private":
            raise GroupOnly()
        return True

    return check(is_not_private_chat_check)


def get_parameters(func: Callable[..., Any], *, ignored: Literal[1, 2] | None = None) -> dict[str, inspect.Parameter]:
    if sys.version_info >= (3, 14):
        signature = inspect.signature(func, annotation_format=inspect.Format.FORWARDREF) # the annotations for ignored parameters may be undefined
    else:
        signature = inspect.signature(func)

    if ignored is None:
        ignored = 2 if func.__qualname__ != func.__name__ and not func.__qualname__.rpartition(".")[0].endswith("<locals>") else 1

    if len(signature.parameters) < ignored:
        raise TypeError(f"Callback with at least {ignored} parameter(s) expected, but given callback only takes {len(signature.parameters)}.")

    params = {}

    for name, value in list(signature.parameters.items())[ignored:]:
        if isinstance(value.annotation, ForwardRef):
            # this will certainly fail if the ForwardRef was created by calling __annotate__(2)
            value = value.replace(annotation=eval(value.annotation.__forward_arg__, func.__globals__))
        elif isinstance(value.annotation, str):
            value = value.replace(annotation=eval(value.annotation, func.__globals__))

        params[name] = value

    return params
