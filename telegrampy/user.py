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

import html
import io
from typing import TYPE_CHECKING, Optional, Union

from .abc import TelegramObject
from .mixins import Hashable
from .utils import escape_markdown

if TYPE_CHECKING:
    from .http import HTTPClient
    from .message import Message
    from .utils import ParseMode
    from .types.user import User as UserPayload


class User(TelegramObject, Hashable):
    """Represents a Telegram user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: str(x)

            Returns the user's name.

    Attributes
    ----------
    id: :class:`int`
        The ID of the user.
    is_bot: :class:`bool`
        If the user is a bot.
    first_name: :class:`str`
        The first name of the user, if exists.
    last_name: Optional[:class:`str`]
        The last name of the user, if exists.
    username: Optional[:class:`str`]
        The username of the user, if applicable.
    language_code: Optional[:class:`str`]
        The IETF language tag for the user's language, if applicable.
    added_to_attachment_menu: :class:`bool`
        Whether the logged in bot is added to this user's attachment menu.  
    is_premium: :class:`bool`
        Whether the user is subscribed to Telegram Premium.
    can_join_groups: :class:`bool`
        Whether the logged in bot can join groups. Only returned in :class:`telegrampy.Client.get_me`.
    can_read_all_group_messages: :class:`bool`
        Whether privacy mode is disabled for the logged in bot. Only returned in :class:`telegrampy.Client.get_me`.
    supports_inline_queries: :class:`bool`
        Whether the logged in bot has inline queries enabled. Only returned in :class:`telegrampy.Client.get_me`.
    can_connect_to_business: :class:`bool`
        Whether the logged in bot can be connected to a Telegram business account to receive its messages.
    has_main_web_app: :class:`bool`
        Whether the logged in bot has a main web app.
    """

    if TYPE_CHECKING:
        id: int
        is_bot: bool
        username: Optional[str]
        first_name: str
        last_name: Optional[str]
        language_code: Optional[str]
        is_premium: bool
        added_to_attachment_menu: bool
        can_join_groups: bool
        can_read_all_group_messages: bool
        supports_inline_queries: bool
        can_connect_to_business: bool
        has_main_web_app: bool

    def __init__(self, http: HTTPClient, data: UserPayload) -> None:
        super().__init__(http)
        self.id: int = data.get("id")
        self.is_bot: bool = data.get("is_bot")
        self.username: Optional[str] = data.get("username")
        self.first_name: str = data.get("first_name")
        self.last_name: Optional[str] = data.get("last_name")
        self.language_code: Optional[str] = data.get("language_code")
        self.is_premium: bool = data.get("is_premium", False)
        self.added_to_attachment_menu: bool = data.get("added_to_attachment_menu", False)
        self.can_join_groups: bool = data.get("can_join_groups", False)
        self.can_read_all_group_messages: bool = data.get("can_read_all_group_messages", False)
        self.supports_inline_queries: bool = data.get("supports_inline_queries", False)
        self.can_connect_to_business: bool = data.get("can_connect_to_business", False)
        self.has_main_web_app: bool = data.get("has_main_web_app", False)

    def __str__(self) -> Optional[str]:
        return self.username

    @property
    def name(self) -> str:
        """:class:`str`: Username if the user has one. Otherwise the full name of the user."""

        return self.username or self.full_name

    @property
    def full_name(self) -> str:
        """:class:`str`: The user's full name."""

        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    @property
    def link(self) -> Optional[str]:
        """Optional[:class:`str`]: The t.me link for the user, if applicable."""

        return f"http://t.me/{self.username}" if self.username else None

    def mention(self, text: Optional[str] = None, parse_mode: ParseMode = "HTML") -> str:
        """Returns a mention for the user.

        Parameters
        ----------
        text: :class:`str`
            The mention text.
        parse_mode: :class:`str`
            The parse mode for the mention.

        Returns
        -------
        :class:`str`:
            The mention string.
        """

        if not text:
            text = self.name

        if parse_mode == "HTML":
            return f'<a href="tg://user?id={self.id}">{html.escape(text)}</a>'
        elif parse_mode == "Markdown":
            return f"[{escape_markdown(text, version=1)}](tg://user?id={self.id})"
        elif parse_mode == "MarkdownV2":
            return f"[{escape_markdown(text, version=2)}](tg://user?id={self.id})"

    async def send(self, content: str, parse_mode: Optional[ParseMode] = None) -> Message:
        """|coro|

        Sends a message to the user.

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
        parse_mode: Optional[ParseMode] = None
    ) -> Message:
        """|coro|

        Sends a document to the user.

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

        Sends a photo to the user.

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
