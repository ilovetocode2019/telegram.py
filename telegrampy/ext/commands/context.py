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

from typing import TYPE_CHECKING, Any, Coroutine, Dict, Generic, List, Optional, TypeVar, Union

from telegrampy.abc import Messageable

if TYPE_CHECKING:
    from telegrampy.chat import Chat
    from telegrampy.message import Message
    from telegrampy.user import User
    from telegrampy.utils import ParseMode
    from .bot import Bot
    from .cog import Cog
    from .core import Command

    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    ContextT = TypeVar("ContextT", bound="Context")
    CommandT = TypeVar("CommandT", bound="Command")
    CogT = TypeVar("CogT", bound="Cog")

BotT = TypeVar("BotT", bound="Bot")


class Context(Messageable, Generic[BotT]):
    """Context for a command.

    Attributes
    ----------
    bot: :class:`telegrampy.ext.commands.Bot`
        The bot that created the context.
    message: :class:`telegrampy.Message`
        The message the invoked the command.
    command: :class:`telegrampy.Command`
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
        The kwargs passed into the command.
    """

    def __init__(
        self,
        *,
        bot: BotT,
        message: Message,
        command: Optional[Command],
        invoked_with: str,
        chat: Chat,
        author: User,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ):
        self.bot: BotT = bot
        self.message: Message = message
        self.command: Optional[Command] = command
        self.invoked_with: str = invoked_with
        self.chat: Chat = chat
        self.author: User = author
        self.args: List[Any] = args or []
        self.kwargs: Dict[str, Any] = kwargs or {}
        self.command_failed: Optional[bool] = None

    @property
    def _chat_id(self):
        return self.chat.id

    @property
    def _http_client(self):
        return self.bot.http

    async def reply(self, content: str, parse_mode: Optional[ParseMode] = None) -> Message:
        """|coro|

        Replys to the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        parse_mode: :class:`str`
            The parse mode of the message to send.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the message failed.
        """

        return await self.message.reply(content=content, parse_mode=parse_mode)
