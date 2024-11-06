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
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Generic, List, Optional, TypeVar, Union

from telegrampy import Chat, User

from . import errors
from .context import Context
from .converter import ChatConverter, Converter, UserConverter

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    from .bot import Bot
    from .cog import Cog

    ContextT = TypeVar("ContextT", bound="Context")
    CommandT = TypeVar("CommandT", bound="Command")

T = TypeVar("T")
Coro = Coroutine[Any, Any, T]
CoroFunc = Callable[..., Coro[Any]]
MaybeCoro = Union[T, Coro[T]]
Check = Callable[[Context[Any]], MaybeCoro[bool]]

CogT = TypeVar("CogT", bound="Cog")

if TYPE_CHECKING:
    P = ParamSpec("P")
else:
    P = TypeVar("P")


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
        func: Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ],
        **kwargs
    ) -> None:
        self.callback = func

        signature = inspect.signature(func)
        self.params: Dict[str, inspect.Parameter] = signature.parameters.copy()

        # Support for PEP-585
        for key, value in self.params.items():
            if isinstance(value.annotation, str):
                self.params[key] = value = value.replace(annotation=eval(value.annotation, function.__globals__))

        self._data: Any = kwargs
        self.name: str = kwargs.get("name") or func.__name__
        self.description: Optional[str] = kwargs.get("description")
        self.usage: Optional[str] = kwargs.get("usage")
        self.aliases: List[str] = kwargs.get("aliases") or []
        self.hidden: bool = kwargs.get("hidden") or False
        self.cog: Optional[Cog] = None
        self.bot: Optional[Bot] = None
        self.checks: List[Check] = []

    def __str__(self) -> str:
        return self.name

    @property
    def clean_params(self) -> Dict[str, inspect.Parameter]:
        """Dict[:class:`str`, :class:`inspect.Parameter`]:
            Returns a mapping similar to :attr:`inspect.Signature.parameters`,
            but without self or context.
        """
        params = self.params.copy()

        # if in a cog, the first parameter is self
        if self.cog is not None:
            try:
                del params[next(iter(params))]
            except StopIteration:
                raise ValueError("Missing self parameter") from None

        # the context parameter is always first/next
        try:
            del params[next(iter(params))]
        except StopIteration:
            raise ValueError("missing context parameter") from None

        return params

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

        params = self.clean_params

        if not params:
            return ""

        final = []
        for name, param in params.items():
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

    async def _convert_argument(self, ctx: Context, argument: str, param: inspect.Parameter) -> Any:
        # Get the converter for the argument
        if param.annotation == inspect._empty:
            converter = str if param.default == inspect._empty or param.default is None else type(param.default)
        else:
            converter = param.annotation
            if converter == User:
                converter = UserConverter()
            elif converter == Chat:
                converter = ChatConverter()

        # If the converter is a subclass of Converter, then create an instance
        if inspect.isclass(converter) and issubclass(converter, Converter):
            converter = converter()

        # If the converter is a Converter instance, use the convert method to convert
        if isinstance(converter, Converter):
            try:
                return await converter.convert(ctx, argument)
            except errors.CommandError:
                raise
            except Exception as exc:
                raise errors.ConversionError(converter, exc) from exc

        # Otherwise just use the converter as a callable
        try:
            return converter(argument)
        except errors.CommandError:
            raise
        except Exception as exc:
            try:
                name = converter.__name__
            except AttributeError:
                name = converter.__class__.__name__  # type: ignore
            raise errors.BadArgument(f"Converting to '{name}' failed for parameter '{param.name}'") from exc

    async def _parse_arguments(self, ctx: Context) -> None:
        if not ctx.message or not ctx.message.content:
            raise RuntimeError  # TODO: better solution?

        # Prepare parameters
        ctx.args = [ctx] if not self.cog else [self.cog, ctx]
        iterator = iter(self.params.items())

        # Prepare input
        text, = ctx.message.content.split(" ", 1)[1:] or ("",)
        parser = ArgumentParser(text)

        # Eat cog parameter if any
        if self.cog:
            try:
                next(iterator)
            except StopIteration:
                raise errors.CommandError(f"Callback for {self} command is missing 'self' parameter")

        # Eat ctx parameter
        try:
            next(iterator)
        except StopIteration:
            raise errors.CommandError(f"Callback for {self} command is missing 'ctx' parameter")

        # The remaining parameters in the iterator need to be filled with arguments
        for name, param in iterator:
            if param.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
                argument = parser.argument()
                if argument:
                    argument = await self._convert_argument(ctx, argument, param)
                elif not argument and param.default == inspect._empty:
                    raise errors.MissingRequiredArgument(param)

                ctx.args.append(argument or param.default)

            elif param.kind == inspect._ParameterKind.KEYWORD_ONLY:
                argument = parser.keyword_argument()
                if argument:
                    argument = await self._convert_argument(ctx, argument, param)
                elif not argument and param.default == inspect._empty:
                    raise errors.MissingRequiredArgument(param)

                ctx.kwargs[param.name] = argument or param.default

            elif param.kind == inspect._ParameterKind.VAR_POSITIONAL:
                arguments = parser.extras()
                arguments = [await self._convert_argument(ctx, argument, param) for argument in arguments]
                ctx.args.extend(arguments)

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

        # Run command checks
        for check in self.checks:
            if not check(ctx):
                return False

        # Run cog check if any
        if self.cog:
            if not self.cog.cog_check(ctx):
                return False

        # When everything passes, return True
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
            raise errors.CheckFailure("The checks for this command failed")

        await self._parse_arguments(ctx)

        try:
            return await self.callback(*ctx.args, **ctx.kwargs)  # type: ignore
        except Exception as exc:
            ctx.command_failed = True
            raise errors.CommandInvokeError(exc) from exc


class ArgumentParser:
    def __init__(self, buffer):
        self.index = 0
        self.buffer = buffer
        self.legnth = len(buffer)

    def argument(self):
        pos = 0
        in_quotes = False
        result = ""

        while True:
            try:
                current = self.buffer[self.index + pos]
                pos += 1
                if current == " " and result.strip(" ") and not in_quotes:
                    self.index += pos
                    break
                elif current == '"':
                    in_quotes = True if not in_quotes else False
                else:
                    result += current

            except IndexError:
                self.index = self.legnth
                if in_quotes:
                    raise errors.ExpectedClosingQuote() from None

                if not result.strip(" "):
                    result = ""
                break

        return result

    def keyword_argument(self):
        result = self.buffer[self.index:]
        self.index == self.legnth

        if not result.strip(" "):
            return ""
        return result

    def extras(self):
        arguments = []
        while True:
            argument = self.argument()
            if argument:
                arguments.append(argument)
            else:
                break

        return arguments


def command(
    *args: Any,
    **kwargs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ],
    ], Command[CogT, P, T]]:
    """Turns a function into a command.

    See :class:`telegrampy.ext.commands.Command`
    for parameters.
    """

    def deco(
        func: Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ],
    ) -> Command[CogT, P, T]:
        kwargs["name"] = kwargs.get("name")

        command = Command(func, **kwargs)
        command.checks = getattr(func, "_command_checks", [])

        command = Command(func, **kwargs)
        return command

    return deco


def check(check_function: Check) -> Callable[[T], T]:
    """Makes a check for a command."""

    def deco(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func.add_check(check_function)
        else:
            if not getattr(func, "_command_checks", None):
                func._command_checks = [check_function]
            else:
                func._command_checks.append(check_function)
        return func

    return deco  # type: ignore


def is_owner() -> Callable[[T], T]:
    """A command check for checking that the user is the owner."""

    def is_owner_check(ctx: Context) -> bool:
        if ctx.author.id not in (ctx.bot.owner_ids or [ctx.bot.owner_id]):
            raise errors.NotOwner("You must be the owner to use this command")
        return True

    return check(is_owner_check)


def is_private_chat() -> Callable[[T], T]:
    """A command check for checking that the chat is a private chat."""

    def is_private_chat_check(ctx: Context) -> bool:
        if ctx.chat.type != "private":
            raise errors.PrivateChatOnly()
        return True

    return check(is_private_chat_check)


def is_not_private_chat() -> Callable[[T], T]:
    """A command check for checking that the chat is not a private chat."""

    def is_not_private_chat_check(ctx: Context) -> bool:
        if ctx.chat.type == "private":
            raise errors.GroupOnly()
        return True

    return check(is_not_private_chat_check)
