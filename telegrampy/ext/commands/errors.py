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
from typing import TYPE_CHECKING

from telegrampy import TelegramException

if TYPE_CHECKING:
    from .converter import Converter


class CommandError(TelegramException):
    """Base exception for all command errors.

    This inherits from :exc:`telegrampy.TelegramException`.
    """


class CommandNotFound(CommandError):
    """Raised when a command is not found.

    This inherits from :exc:`telegrampy.ext.commands.CommandError`.
    """


class CommandRegistrationError(CommandError):
    """Raised when a command cannot be registered, because it's name is already being used.

    This inherits from :exc:`telegrampy.ext.commands.CommandError`.

    Attributes
    ----------
    name: :class:`str`
        The command name that had a conflict.
    alias_conflict: :class:`bool`
        Whether the command name was an alias of the command being added.
    """

    def __init__(self, name: str, *, alias_conflict: bool = False) -> None:
        self.name: str = name
        self.alias_conflict: bool = alias_conflict
        super().__init__(f"The {'alias' if alias_conflict else 'command'} {name} is already registered as a command name or alias.")


class ExtensionError(CommandError):
    """Base exception for extension related errors.

    This inherits from :exc:`telegrampy.ext.commands.CommandError`.
    """


class ExtensionAlreadyLoaded(ExtensionError):
    """Raised when an extension is already loaded.

    This inherits from :exc:`telegrampy.ext.commands.ExtensionError`.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Extension {name} is already loaded")


class ExtensionNotLoaded(ExtensionError):
    """Raised when an extension is not loaded.

    This inherits from :exc:`telegrampy.ext.commands.ExtensionError`.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Extension {name} has not been loaded")


class ExtensionNotFound(ExtensionError):
    """Raised when an extension is not found.

    This inherits from :exc:`telegrampy.ext.commands.ExtensionError`.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Extension {name} could not be loaded")


class NoEntryPointError(ExtensionError):
    """Raised when an extension has no `setup` function.

    This inherits from :exc:`telegrampy.ext.commands.ExtensionError`.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Extension {name} has no setup function")


class ExtensionFailed(ExtensionError):
    """Raised when an extension fails.

    This inherits from :exc:`telegrampy.ext.commands.ExtensionError`.

    Attributes
    ---------
    name: :class:`str`
        The extension that failed.
    original: :class:`Exception`
        The original error that was raised.
    """

    def __init__(self, name: str, original: Exception) -> None:
        self.name = name
        self.original = original
        super().__init__(f"Extension raised an exception: {original.__class__.__name__}: {original}")


class UserInputError(CommandError):
    """Base exception for errors that involve user input.

    This inherits from :exc:`telegrampy.ext.commands.CommandError`.
    """


class MissingRequiredArgument(UserInputError):
    """Raised when a required argument is missing.

    This inherits from :exc:`telegrampy.ext.commands.UserInputError`.

    Attributes
    ----------
    param: :class:`inspect.Parameter`
        The argument that is missing.
    """

    def __init__(self, param: inspect.Parameter) -> None:
        self.param = param
        super().__init__(f"'{param}' is a required argument that is missing")


class ConversionError(CommandError):
    """Raised when a :class:`telegrampy.ext.commands.Converter` fails.

    This inherits from :exc:telegrampy.ext.commands.UserInputError`.

    Attributes
    ----------
    converter: :class:`telegrampy.ext.commands.Converter`
        The converter that failed.
    original: :class:`Exception`
        The original error that was failed.
    """

    def __init__(self, converter: Converter, original: Exception) -> None:
        self.converter = converter
        self.original = original
        super().__init__(f"Converter raised an exception: {original.__class__.__name__}: {original}")


class BadArgument(UserInputError):
    """Raised when a bad argument is given.

    This inherits from :exc:`telegrampy.ext.commands.UserInputError`.

    Attributes
    ----------
    arg: :class:`str`
        The bad argument.
    converter: :class:`str`
        The name of the converter that failed.
    """


class ArgumentParsingError(UserInputError):
    """Base exception for argument parsing errors.

    This inherits from :exc:`telegrampy.ext.commands.UserInputError`.
    """


class ExpectedClosingQuote(ArgumentParsingError):
    """Raised when the argument parser expects a closing quote but can't find one.

    This inherits from :exc:`telegrampy.ext.commands.ArgumentParsingError`.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Expected a closing quote")


class CheckFailure(CommandError):
    """Raised when a check fails.

    This inherits from :exc:`telegrampy.ext.commands.CheckFailure`.
    """


class NotOwner(CheckFailure):
    """Raised when a user is not the owner of the bot.

    This inherits from :exc:`telegrampy.ext.commands.CheckFailure`.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Only the owner can use this command")


class PrivateChatOnly(CheckFailure):
    """Raised when a command can only be used in private chats.

    This inherits from :exc:`telegrampy.ext.commands.CheckFailure`.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "This command can only be used in private messages")


class GroupOnly(CheckFailure):
    """Raised when a command can only be used in groups.

    This inherits from :exc:`telegrampy.ext.commands.CheckFailure`.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "This command can only be used in groups")


class CommandInvokeError(CommandError):
    """Raised when a command fails.

    This inherits from :exc:`telegrampy.ext.commands.CommandError`.

    Attributes
    ---------
    original: :class:`Exception`
        The original error that was raised.
    """

    def __init__(self, original: Exception) -> None:
        self.original = original
        super().__init__(f"Command raised an exception: {original.__class__.__name__}: {original}")
