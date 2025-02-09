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

from typing import TYPE_CHECKING, Any

from telegrampy.chat import Chat
from telegrampy.errors import HTTPException, BadRequest
from telegrampy.member import Member
from .errors import BadArgument

if TYPE_CHECKING:
    from .context import Context


class Converter:
    """The base class for custom converters that require :class:`.Context` in order to function."""

    async def convert(self, ctx: Context, argument: str) -> Any:
        """|coro|

        Does the converting.
        """

        raise NotImplementedError


class ChatConverter(Converter):
    """Converts an argument into a :class:`telegrampy.Chat`."""

    async def convert(self, ctx: Context, argument: str) -> Chat:
        try:
            chat_id = int(argument)
        except ValueError:
            chat_id = argument if argument.startswith("@") else f"@{argument}"

        try:
            return await ctx.bot.get_chat(chat_id)
        except BadRequest as exc:
            raise BadArgument(f"Chat '{argument}' is not found") from exc
        except HTTPException as exc:
            raise BadArgument(f"Error while fetching chat '{argument}'") from exc


class MemberConverter(Converter):
    """Converts an argument into a :class:`telegrampy.Member`."""

    async def convert(self, ctx: Context, argument: str) -> Member:
        try:
            user_id = int(argument)
        except ValueError:
            raise BadArgument(f"User '{argument}' is not an ID")

        try:
            return await ctx.chat.get_member(user_id)
        except BadRequest as exc:
            raise BadArgument(f"User '{argument}' not found") from exc
        except HTTPException as exc:
            raise BadArgument(f"Error while fetching user '{argument}'") from exc

MAPPING = {
    Member: MemberConverter,
    Chat: ChatConverter
}
