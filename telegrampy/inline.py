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

from typing import TYPE_CHECKING, Optional

from .abc import TelegramObject
from .location import Location
from .mixins import Hashable
from .user import User

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.inline import InlineQuery as InlineQueryPayload


class InlineQuery(TelegramObject, Hashable):
    """Represents an incoming inline query.

    .. container:: operations

        .. describe:: x == y

            Checks if two inline queries are the same.

        .. describe:: x != y

            Checks if two inline queries are not the same.

        .. describe:: str(x)

            Returns the content of the inline query

    Attributes
    ----------
    id: :class:`str`
        The unique identifier for the query.
    author: :class:`str`
        The sender of the query.
    content: :class:`str`
        The content of the query.
    chat_type: Optional[:class:`str`]
        The type of chat that the inline query was called in.
    location: Optional[:class:`telegrampy.Location`]
        The location of the sender, if set up to be requested.
    """

    id: str
    author: User
    content: str
    offset: str
    chat_type: Optional[str]
    location: Optional[str]

    def __init__(self, http: HTTPClient, data: InlineQueryPayload):
        super().__init__(http, data)

        self.id: str = data.get("id")
        self.author: User = User(data.get("user"))
        self.content: str = data.get("query")
        self.offset: str = data.get("offset")
        self.chat_type: Optional[str] = data.get("chat_type")
        self.location: Optional[str] = data.get("location")

    def __str__(self):
        return self.content
