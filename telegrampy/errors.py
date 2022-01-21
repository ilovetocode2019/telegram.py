"""
MIT License

Copyright (c) 2020-2021 ilovetocode

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

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import aiohttp


class TelegramException(Exception):
    """Base exception for all errors."""


class HTTPException(TelegramException):
    """Raised when an HTTP request fails.

    This inherits from :exc:`telegrampy.TelegramException`.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response for the request that failed.
    messsage: Optional[:class:`str`]
       The message for the request that failed.
    """

    def __init__(self, response: aiohttp.ClientResponse, message: Optional[str]):
        self.response = response
        self.message = message
        super().__init__(f"{response.status} {message}")


class BadRequest(HTTPException):
    """Raised when a bad request is made.

    This inherits from :exc:`telegrampy.HTTPException`.
    """


class InvalidToken(HTTPException):
    """Raised when a token is invalid.

    This inherits from :exc:`telegrampy.HTTPException`.
    """


class Forbidden(HTTPException):
    """Raised when something is forbidden.

    This inherits from :exc:`telegrampy.HTTPException`.
    """


class Conflict(HTTPException):
    """Raised when another instance of the bot is running.

    This inherits from :exc:`telegrampy.HTTPException`.
    """


class ServerError(HTTPException):
    """Raised when telegram returns a 500 error.

    This inherits from :exc:`telegrampy.HTTPException`.
    """
