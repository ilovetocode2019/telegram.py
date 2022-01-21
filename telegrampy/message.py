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

import datetime
from typing import TYPE_CHECKING, Optional

from .abc import TelegramObject
from .chat import Chat
from .mixins import Hashable
from .user import User

if TYPE_CHECKING:
    from .http import HTTPClient
    from .utils import ParseMode
    from .types.message import Message as MessagePayload


class Message(TelegramObject, Hashable):
    """Represents a message in Telegram.

    .. container:: operations

        .. describe:: x == y

            Checks if two messages are equal.

        .. describe:: x != y

            Checks if two messages are not equal.

    Attributes
    ----------
    id: :class:`int`
        The ID of the message.
    created_at: :class:`datetime.datetime`
        The time the message was created.
    edited_at: Optional[:class:`datetime.datetime`]
        The time the message was edited.
    content: :class:`str`
        The content of the message.
    chat: :class:`telegrampy.Chat`
        The chat the message is in.
    author: :class:`telegrampy.User`
        The author of the message.
    """

    if TYPE_CHECKING:
        id: int
        created_at: Optional[datetime.datetime]
        edited_at: Optional[datetime.datetime]
        content: Optional[str]
        chat: Chat
        author: Optional[User]

    def __init__(self, http: HTTPClient, data: MessagePayload):
        super().__init__(http)
        self.id: int = data.get("message_id")

        created_at: int = data.get("date")
        self.created_at: Optional[datetime.datetime]
        if created_at:
            self.created_at = datetime.datetime.fromtimestamp(created_at)
        else:
            self.created_at = None

        edited_at = data.get("edit_date")
        self.edited_at: Optional[datetime.datetime]
        if edited_at:
            self.edited_at = datetime.datetime.fromtimestamp(edited_at)

        self.content: Optional[str] = data.get("text")
        self.chat: Chat = Chat(http, data.get("chat"))

        self.author: Optional[User]
        if "from" in data:
            self.author = User(http, data.get("from"))  # type: ignore
        else:
            self.author = None

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

        return await self._http.send_message(chat_id=self.chat.id, content=content, parse_mode=parse_mode, reply_message_id=self.id)

    async def forward(self, destination: Chat) -> Message:
        """|coro|

        Forwards the message to a destination.

        Parameters
        ----------
        destination: :class:telegrampy.Chat`
            The chat forward the message to.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Forwarding the message failed.
        """

        return await self._http.forward_message(chat_id=destination.id, from_chat_id=self.chat.id, message_id=self.id)

    async def edit_content(self, content: str, parse_mode: Optional[ParseMode] = None) -> Optional[Message]:
        """|coro|

        Edits the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the new message.
        parse_mode: :class:`str`
            The parse mode of the new message.

        Raises
        ------
        :exc:`telegrampy.HTTException`
            Editing the message failed.
        """

        return await self._http.edit_message_content(chat_id=self.chat.id, message_id=self.id, content=content, parse_mode=parse_mode)

    async def delete(self) -> None:
        """|coro|

        Deletes the message.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Deleting the message failed.
        """

        await self._http.delete_message(chat_id=self.chat.id, message_id=self.id)
