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

import asyncio
import io

from typing import TYPE_CHECKING, Any, Generator, List, Optional, Union

if TYPE_CHECKING:
    from .http import HTTPClient
    from .markup import *
    from .message import Message
    from .poll import Poll
    from .utils import ParseMode

    ReplyMarkup = Union[InlineKeyboard, ReplyKeyboard, ReplyKeyboardRemove, ForceReply]


class Messageable:
    """Represents any Telegram resource that messages can be sent to.

    This is implemented by the following subclasses:

    - :class:`telegrampy.PartialChat`
    - :class:`telegrampy.Chat`
    - :class:`telegrampy.User`
    - :class:`telegrampy.Member`
    - :class:`telegrampy.ext.commands.Context`
    """

    @property
    def _chat_id(self) -> int:
        raise NotImplementedError

    @property
    def _http_client(self) -> HTTPClient:
        raise NotImplementedError

    async def send(
        self,
        content: str,
        *,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        """|coro|

        Sends a message to the destination.

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
        :exc:`errors.HTTPException`
            Sending the message failed.
        """

        from .message import Message
        from .markup import InlineKeyboard

        result = await self._http_client.send_message(
            chat_id=self._chat_id,
            content=content,
            parse_mode=parse_mode,
            reply_markup=reply_markup.to_reply_markup() if reply_markup is not None else None
        )

        ret = Message(self._http_client, result)

        if reply_markup is not None and isinstance(reply_markup, InlineKeyboard):
            self._http_client.inline_keyboard_state.add(ret.id, reply_markup)

        return ret

    async def send_document(
        self,
        document: Union[io.BytesIO, str],
        *,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        """|coro|

        Sends a document to the destination.

        Parameters
        ----------
        document: Union[:class:`io.BytesIO`, :class:`str`]
            The document to send. Either a file or the path to one.
        filename: Optional[:class:`str`]
            The filename of the document.
        caption: Optional[:class:`str`]
            The document's caption.
        parse_mode: Optional[:class:`str`]
            The parse mode for the caption.
        reply_markup: Optional[Union[:class:`InlineKeyboard`, :class:`ReplyKeyboard`, :class:`ReplyKeyboardRemove, :class:`ForceReply`]]
            The reply markup interface to send with the message.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the document failed.
        """

        from .message import Message

        if isinstance(document, str):
            with open(document, "rb") as file:
                content = file.read()
                document = io.BytesIO(content)

        result = await self._http_client.send_document(
            chat_id=self._chat_id,
            file=document,
            filename=filename,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup.to_reply_markup() if reply_markup is not None else None
        )

        ret = Message(self._http_client, result)

        if reply_markup is not None and isinstance(reply_markup, InlineKeyboard):
            self._http_client.inline_keyboard_state.add(ret.id, reply_markup)

        return ret

    async def send_photo(
        self,
        photo: Union[io.BytesIO, str],
        *,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        """|coro|

        Sends a photo to the destination.

        Parameters
        ----------
        photo: Union[:class:`io.BytesIO`, :class:`str`]
            The photo to send. Either a file or the path to one.
        filename: Optional[:class:`str`]
            The filename of the photo.
        caption: Optional[:class:`str`]
            The caption for the photo.
        parse_mode: Optional[:class:`str`]
            The parse mode for the caption.
        reply_markup: Optional[Union[:class:`InlineKeyboard`, :class:`ReplyKeyboard`, :class:`ReplyKeyboardRemove, :class:`ForceReply`]]
            The reply markup interface to send with the message.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the photo failed.
        """

        from .message import Message

        if isinstance(photo, str):
            with open(photo, "rb") as file:
                content = file.read()
                photo = io.BytesIO(content)

        result = await self._http_client.send_photo(
            chat_id=self._chat_id,
            file=photo,
            filename=filename,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup.to_reply_markup() if reply_markup is not None else None
        )

        ret = Message(self._http_client, result)


        if reply_markup is not None and isinstance(reply_markup, InlineKeyboard):
            self._http_client.inline_keyboard_state.add(ret.id, reply_markup)

        return ret

    async def send_poll(
        self,
        question: str,
        options: List[str]
    ) -> Poll:
        """|coro|

        Sends a poll to the destination.

        Parameters
        ----------
        question: :class:`str`
            The question of the poll.
        options: List[:class:`str`]
            The options in the poll.
        reply_markup: Optional[Union[:class:`InlineKeyboard`, :class:`ReplyKeyboard`, :class:`ReplyKeyboardRemove, :class:`ForceReply`]]
            The reply markup interface to send with the message.

        Returns
        -------
        :class:`telegrampy.Poll`
            The poll sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the poll failed.
        """

        from .poll import Poll

        result = await self._http_client.send_poll(
            chat_id=self._chat_id,
            question=question,
            options=options
        )

        return Poll(self._http_client, result)

    def typing(self) -> MessageableAction:
        """Returns a context manager that shows a typing indicicator in the destination.
        This is eqivalent to calling :meth:`.action("typing")`
        """

        return MessageableAction(self, "typing")

    def action(self, action: str) -> MessageableAction:
        """Returns a context manager that sends a chat action to the destination until completed or for up to 5 seconds if called with ``await``.

        Usage: ::

            async with chat.action("typing"):
                # do some computing here

            await chat.send("Done!")

        Usage: ::

            await chat.action("typing")

        Parameters
        ----------
        action: :class:`str`
            The action to send.
        """

        return MessageableAction(self, action)


class MessageableAction:
    def __init__(self, messageable: Messageable, action: str):
        self.messageable = messageable
        self.action = action

    async def action_loop(self) -> None:
        while True:
            await self.messageable._http_client.send_chat_action(
                chat_id=self.messageable._chat_id,
                action=self.action
            )
            await asyncio.sleep(5)

    def __await__(self) -> Generator[None, None, None]:
        sender = self.messageable._http_client.send_chat_action(
            chat_id=self.messageable._chat_id,
            action=self.action
        )
        return sender.__await__()

    def __enter__(self) -> None:
        self.task = self.messageable._http_client.loop.create_task(self.action_loop())
 
    def __exit__(self, *args: List[Any]) -> None:
        self.task.cancel()

    async def __aenter__(self) -> None:
        self.__enter__()

    async def __aexit__(self, *args: List[Any]) -> None:
        self.__exit__()
