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

import asyncio
import io

from .errors import *
from .http import HTTPClient
from .message import Message
from .abc import TelegramObject
from .poll import Poll
from .user import User

from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from .utils import ParseMode
    from .types.chat import Chat as ChatPayload


ChatActionSenderT = TypeVar("ChatActionSenderT", bound="ChatActionSender")


class Chat(TelegramObject):
    """
    Represents a chat in Telegram.

    .. container:: operations

        .. describe:: x == y

            Checks if two chats are equal.

        .. describe:: x != y

            Checks if two chats are not equal.

        .. describe:: str(x)

            Returns the chat's title.


    Attributes
    ----------
    id: :class:`int`
        The ID of the chat.
    title: :class:`str`
        The title of the chat.
    description: Optional[:class:`str`]
        The description of the chat.
    type: :class:`str`
        The type of the chat.
    """

    if TYPE_CHECKING:
        title: str
        username: str
        description: str
        type: int

    def __init__(self, http: HTTPClient, data: ChatPayload) -> None:
        super().__init__(http, data)
        self.title: str = data.pop("title")
        self.username: str = data.pop("username")
        self.description: str = data.pop("description")
        self.type: int = data.pop("type")

    def __str__(self) -> str:
        return self.title

    async def send(self, content: str, parse_mode: Optional[ParseMode] = None) -> Message:
        """|coro|

        Sends a message to the chat.

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
        :exc:`errors.HTTPException`
            Sending the message failed.
        """

        return await self._http.send_message(chat_id=self.id, content=content, parse_mode=parse_mode)

    async def send_document(
        self,
        document: Union[io.BytesIO, str],
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> Message:
        """|coro|

        Sends a document to the chat.

        Parameters
        ----------
        document: Union[class:`io.BytesIO`, :class:`str`]
            The document to send. Either a file or the path to one.
        filename: :class:`str`
            The filename of the document.
        caption: :class:`str`
            The document's caption.
        parse_mode: :class:`str`
            The parse mode for the caption.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the document failed.
        """

        if isinstance(document, str):
            with open(document, "rb") as file:
                content = file.read()
                document = io.BytesIO(content)

        return await self._http.send_document(chat_id=self.id, file=document, filename=filename, caption=caption, parse_mode=parse_mode)

    async def send_photo(
        self,
        photo: Union[io.BytesIO, str],
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> Message:
        """|coro|

        Sends a photo to the chat.

        Parameters
        ----------
        photo: Union[class:`io.BytesIO`, :class:`str`]
            The photo to send. Either a file or the path to one.
        filename: Optional[:class:`str`]
            The filename of the photo.
        caption: Optional[:class:`str`]
            The caption for the photo.
        parse_mode: Optional[:class:`str`]
            The parse mode for the caption.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the photo failed.
        """

        if isinstance(photo, str):
            with open(photo, "rb") as file:
                content = file.read()
                photo = io.BytesIO(content)

        return await self._http.send_photo(chat_id=self.id, file=photo, filename=filename, caption=caption, parse_mode=parse_mode)

    async def send_poll(self, question: str, options: List[str]) -> Poll:
        """|coro|

        Sends a poll to the chat.

        Parameters
        ----------
        question: :class:`str`
            The question of the poll.
        options: :class:`list`
            The options in the poll.

        Returns
        -------
        :class:`telegrampy.Poll`
            The poll sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the poll failed.
        """

        return await self._http.send_poll(chat_id=self.id, question=question, options=options)

    async def send_action(self, action: str) -> None:
        """|coro|

        Sends an action to the chat.

        Parameters
        ----------
        action: :class:`str`
            The action to send.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the action failed.
        """

        await self._http.send_chat_action(chat_id=self.id, action=action)

    def action(self, action: str) -> ChatActionSender:
        """
        Returns a context manager that sends a chat action until the with statment is completed.

        Parameters
        ----------
        action: :class:`str`
            The action to send.
        """

        return ChatActionSender(self, action)

    async def get_member(self, user_id: int) -> User:
        """|coro|

        Fetches a member in the chat.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID of the member.

        Returns
        -------
        :class:`telegrampy.User`
            The member fetched.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Fetching the member failed.
        """

        return await self._http.get_chat_member(chat_id=self.id, user_id=user_id)


class ChatActionSender:
    def __init__(self, chat: Chat, action: str) -> None:
        self.chat = chat
        self.action = action

    async def action_loop(self) -> None:
        while True:
            await self.chat.send_action(self.action)
            await asyncio.sleep(5)

    def __enter__(self: ChatActionSenderT) -> ChatActionSenderT:
        self.task = self.chat._http.loop.create_task(self.action_loop())
        return self

    def __exit__(self, *args: Any) -> None:
        self.task.cancel()

    async def __aenter__(self: ChatActionSenderT) -> ChatActionSenderT:
        return self.__enter__()

    async def __aexit__(self, *args) -> None:
        return self.__exit__()
