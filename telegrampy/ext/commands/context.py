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

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from telegrampy.abc import Messageable

if TYPE_CHECKING:
    from telegrampy.chat import Chat
    from telegrampy.markup import *
    from telegrampy.message import Message
    from telegrampy.user import User
    from telegrampy.utils import ParseMode
    from .bot import Bot
    from .core import Command

    ReplyMarkup = InlineKeyboard | ReplyKeyboard | ReplyKeyboardRemove | ForceReply

BotT = TypeVar("BotT", bound="Bot")


class Context(Messageable, Generic[BotT]):
    """Context for a command.

    Attributes
    ----------
    bot: :class:`.Bot`
        The bot that created the context.
    message: :class:`telegrampy.Message`
        The message the invoked the command.
    command: :class:`.Command`
        The command that is being invoked.
    invoked_with: :class:`str`
        The text that triggered the invocation.
    chat: :class:`telegrampy.Chat`
        The chat the command is being invoked in.
    author: :class:`telegrampy.User`
        The author invoking the command.
    command_failed: :class:`bool`
        If the command failed or not.
    args: :class:`list`
        The arguments passed into the command.
    kwargs: :class:`dict`
        The keyword arguments passed into the command.
    """

    def __init__(
        self,
        *,
        bot: BotT,
        message: Message,
        command: Command | None,
        invoked_with: str,
        chat: Chat,
        author: User,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None
    ) -> None:
        self.bot: BotT = bot
        self.message: Message = message
        self.command: Command | None = command
        self.invoked_with: str = invoked_with
        self.chat: Chat = chat
        self.author: User = author
        self.args: list[Any] = args if args is not None else []
        self.kwargs: dict[str, Any] = kwargs if kwargs is not None else {}
        self.command_failed: bool | None = None

    @property
    def _chat_id(self) -> int:
        return self.chat.id

    @property
    def _http_client(self) -> HTTPClient:
        return self.bot.http

    async def reply(self, content: str, *, parse_mode: ParseMode | None = None, reply_markup: ReplyMarkup | None = None) -> Message:
        """|coro|

        Replys to the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        parse_mode: :class:`str` | None
            The parse mode of the message to send.
        reply_markup: :class:`InlineKeyboard` | :class:`ReplyKeyboard` | :class:`ReplyKeyboardRemove` | :class:`ForceReply` | None
            The reply markup interface to send with the message.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the message failed.
        """

        return await self.message.reply(content, parse_mode=parse_mode, reply_markup=reply_markup)
