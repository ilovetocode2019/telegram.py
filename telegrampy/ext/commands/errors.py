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

from telegrampy import TelegramException


class CommandError(TelegramException):
    """Base exception for all command errors."""

    pass

class CommandNotFound(CommandError):
    """Raised when a command is not found."""

    pass

class CommandRegistrationError(CommandError):
    """Raised when a command cannot be registered."""

    pass

class ExtensionNotLoaded(CommandError):
    """
    Raised when an extension is not loaded.

    Attributes
    ----------
    name: :class:`str`
        The name of the extension that is not loaded.
    """

    def __init__(self, name):
        self.name = name
        super().__init__(f"Extension '{name}' has not been loaded")

class ExtensionAlreadyLoaded(CommandError):
    """
    Raised when an extension is already loaded.

    Attributes
    ----------
    name: :class:`str`
        The name of the extension that is already loaded.
    """

    def __init__(self, name):
        self.name = name
        super().__init__(f"Extension '{name}' is already loaded")

class MissingRequiredArgument(CommandError):
    """
    Raised when a required argument is missing.

    Attributes
    ----------
    param: :class:`str`
        The argument that is missing.
    """

    def __init__(self, param):
        self.param = param
        super().__init__(f"'{param}' is a required argument that is missing")

class BadArgument(CommandError):
    """
    Raised when a bad argument is given.

    Attributes
    ----------
    arg: :class:`str`
        The bad argument.
    converter: :class:`str`
        The name of the converter that failed.
    """

    def __init__(self, arg, converter, message=None):
        self.arg = arg
        self.converter = converter
        super().__init__(message or f"Failed to convert '{arg}' to '{converter}'")

class CheckFailure(CommandError):
    """Raised when a check fails."""

    pass

class NotOwner(CheckFailure):
    """Raised when a user is not the owner of the bot."""

    pass

class CommandInvokeError(CommandError):
    """
    Raised when a command fails.

    Attributes
    ---------
    error: :class:`Exception`
         The original error that was raised.
    """

    def __init__(self, error):
        self.error = error
        super().__init__(f"Command raised an exception: {error.__class__.__name__}: {error}")

class PrivateChatOnly(CheckFailure):
    """Raised when a command can only be used in private chats."""

    def __init__(self, message=None):
        super().__init__(message or "This command can only be used in private messages")

class GroupOnly(CheckFailure):
    """Raised when a command can only be used in groups."""

    def __init__(self, message=None):
        super().__init__(message or "This command can only be used in groups")

    pass
