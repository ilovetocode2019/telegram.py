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

class TelegramException(Exception):
    """Base exception for all errors."""

    pass

class HTTPException(TelegramException):
    """
    Raised when an HTTP request fails.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response for the request that failed.
    messsage: Optional[:class:`str`]
       The message for the request that failed.
    """

    def __init__(self, response, message=""):
        self.response = response
        self.message = message
        super().__init__(f"{response.status} {message}")

class InvalidToken(HTTPException):
    """Raised when a token is invalid."""

    def __init__(self, response, message=""):
        super().__init__(response, message)

class Forbidden(HTTPException):
    """Raised when something is forbidden."""

    def __init__(self, response, message=""):
        super().__init__(response, message)

class Conflict(HTTPException):
    """Raised when another instance of the bot is running."""

    def __init__(self, response, message=""):
        super().__init__(response, message)