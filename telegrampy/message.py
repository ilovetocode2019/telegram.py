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

import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from .chat import Chat
from .user import User
from .mixins import Hashable

if TYPE_CHECKING:
    from .chat import PartialChat, Chat
    from .markup import *
    from .user import User
    from .http import HTTPClient
    from .utils import ParseMode
    from .types.message import Message as MessagePayload, MessageEntity as MessageEntityPayload

    ReplyMarkup = Union[InlineKeyboard, ReplyKeyboard, ReplyKeyboardRemove, ForceReply]


class PartialMessage(Hashable):
    """Represents a partial message that can be interacted with, without containing information.

    .. container:: operations

        .. describe:: x == y

            Checks if two partial chats are equal.

        .. describe:: x != y

            Checks if two chats partial are not equal.

    Attributes
    ----------
    id: :class:`int`
        The given ID of the partial chat.
    chat: Union[:class:`telegrampy.PartialChat`, :class:`telegrampy.Chat`]
        The chat the partial message was sent in.
    """

    def __init__(self, message_id: int, chat: Union[PartialChat, Chat]):
        self._http: HTTPClient = chat._http
        self.id: int = message_id
        self.chat: Union[PartialChat, Chat] = chat

    async def reply(
        self,
        content: str,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        """|coro|

        Sends a reply to the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        parse_mode: Optional[:class:`str`]
            The parse mode of the message to send.
        reply_markup: Optional[Union[:class:`InlineKeyboard`, :class:`ReplyKeyboard`, :class:`ReplyKeyboardRemove, :class:`ForceReply`]]
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

        result = await self._http.send_message(
            chat_id=self.chat.id,
            content=content,
            parse_mode=parse_mode,
            reply_markup=reply_markup.to_reply_markup() if reply_markup is not None else None,
            reply_message_id=self.id
        )

        ret = Message(self._http, result)

        if reply_markup is not None and isinstance(reply_markup, InlineKeyboard):
            self._http.inline_keyboard_state.add(ret.id, reply_markup)

        return ret

    async def forward(self, destination: Chat) -> Message:
        """|coro|

        Forwards the message to a destination.

        Parameters
        ----------
        destination: Union[:class:`telegrampy.PartialChat`, :class:`telegrampy.Chat`]
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

        result = await self._http.forward_message(
            chat_id=destination.id,
            from_chat_id=self.chat.id,
            message_id=self.id
        )

        return Message(self._http, result)

    async def edit(
        self,
        *,
        content: str,
        parse_mode: Optional[ParseMode] = None
    ) -> Optional[Message]:
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

        result = await self._http.edit_message_content(
            chat_id=self.chat.id,
            message_id=self.id,
            content=content,
            parse_mode=parse_mode
        )

        if result:
            return Message(self._http, result)

    async def pin(self, *, silent: bool = False) -> None:
        """|coro|

        Pins the message to the chat.

        Parameters
        ----------
        silent: :class:`bool`
            Whether to not notify chat members when a message is sent.
            Notifications are never sent for channels and private chats.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Pinning the message failed.
        """

        await self._http.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.id,
            disable_notification=silent
        )

    async def unpin(self) -> None:
        """|coro|

        Unpins the message from the chat.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Unpinning the message failed.
        """

        await self._http.unpin_chat_message(
            chat_id=self.chat.id,
            message_id=self.id
        )

    async def delete(self) -> None:
        """|coro|

        Deletes the message.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Deleting the message failed.
        """

        await self._http.delete_message(chat_id=self.chat.id, message_id=self.id)


class Message(PartialMessage):
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
    thread_id: Optional[:class:`int`]
        The ID of the thread the message was sent in.
    author: Optional[:class:`int`]
        The user who sent the message.
    created_at: :class:`datetime.datetime`
        The time the message was created.
    edited_at: Optional[:class:`datetime.datetime`]
        The time the message was edited.
    content: Optional[:class:`str`]
        The content of the message, for text messages.
    chat: :class:`telegrampy.Chat`
        The chat the message was sent in.
    """

    def __init__(self, http: HTTPClient, data: MessagePayload):
        self._http: HTTPClient = http
        self.id: int = data["message_id"]
        self.thread_id: Optional[int] = data.get("message_thread_id")
        self.author: Optional[User] = User(http, data["from"]) if "from" in data else None

        self.created_at: datetime.datetime = datetime.datetime.fromtimestamp(
            data["date"],
            tz=datetime.timezone.utc
        )

        self.edited_at: Optional[datetime.datetime] = (
            datetime.datetime.fromtimestamp(data["edit_date"], tz=datetime.timezone.utc)
            if "edit_date" in data
            else None
        )

        self.content: Optional[str] = data.get("text")
        self.chat: Chat = Chat(http, data.get("chat"))

        self.entities: List[MessageEntity] = [
            MessageEntity(http, entity, text=self.content)
            for entity in data.get("entities", [])
        ]


class MessageEntity:
    """Represents a message entity.

    Attributes
    ----------
    type: :class:`str`
        The type of entity.
    offset: :class:`int`
        The offset of the start of the entity.
    length: :class:`int`
        The length of the entity.
    url: Optional[:class:`str`]
        The URL that will be opened, for `text_link`.
    user: Optional[:class:`telegrampy.User`]
        The mentioned user for `text_mention`.
    language: Optional[:class:`str`]
        The programming language of the entity text, for `pre`.
    custom_emoji_id: Optional[:class:`str`]
        The ID, for custom_emoji.
    value: :class:`str`
        The text value of the message entity.
    """

    def __init__(self, http: HTTPClient, data: MessageEntityPayload, *, text: str):
        self._http: HTTPClient = http
        self.type: str = data["type"]
        self.offset: int = data["offset"]
        self.length: int = data.get("length")
        self.url: Optional[str] = data.get("url")
        self.user: Optional[User] = User(http, data["user"]) if "user" in data else None
        self.language: Optional[str] = data.get("language")
        self.custom_emoji_id: Optional[str] = data.get("custom_emoji_id")
        self.value: str = text[self.offset:self.offset+self.length]
