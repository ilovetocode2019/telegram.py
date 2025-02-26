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
from typing import TYPE_CHECKING

from telegrampy.file import PhotoSize

from .abc import Messageable
from .mixins import Hashable
from .utils import escape_markdown

if TYPE_CHECKING:
    from .http import HTTPClient
    from .utils import ParseMode
    from .types.user import User as UserPayload, UserProfilePhotos as UserProfilePhotosPayload


class BaseUser(Hashable):
    def __init__(self, http: HTTPClient, data: UserPayload) -> None:
        self._http: HTTPClient = http
        self.id: int = data.get("id")
        self.is_bot: bool = data.get("is_bot")
        self.username: str | None = data.get("username")
        self.first_name: str = data.get("first_name")
        self.last_name: str | None = data.get("last_name")
        self.language_code: str | None = data.get("language_code")
        self.is_premium: bool = data.get("is_premium", False)
        self.added_to_attachment_menu: bool = data.get("added_to_attachment_menu", False)

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """:class:`str`: Username if the user has one. Otherwise the full name of the user."""

        return self.username or self.full_name

    @property
    def full_name(self) -> str:
        """:class:`str`: The user's full name."""

        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    @property
    def link(self) -> str | None:
        """:class:`str` | None: The t.me link for the user, if applicable."""

        return f"http://t.me/{self.username}" if self.username else None

    def mention(self, text: str | None = None, parse_mode: ParseMode = "HTML") -> str:
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

    async def get_profile_photos(self, *, offset: int | None = None, limit: int = 100) -> UserProfilePhotos:
        """Fetches the profile pictures for the user.

        Parameters
        ----------
        offset: :class:`int` | None
            The sequential number of the first photo to be retrieved.
            If unspecified, all photos will be retrieved.
        limit: :class:`int`
            The maximum number of photos to be retrieved. Defaults to and cannot exceed ``100``.
        """
        
        result = await self._http.get_user_profile_photos(user_id=self.id, offset=offset, limit=limit)
        return UserProfilePhotos(self._http, result)

class User(BaseUser, Messageable):
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
        Whether the user is a bot.
    first_name: :class:`str`
        The first name of the user, if exists.
    last_name: :class:`str` | None
        The last name of the user, if exists.
    username: :class:`str` | None
        The username of the user, if applicable.
    language_code: :class:`str` | None
        The IETF language tag for the user's language, if applicable.
    added_to_attachment_menu: :class:`bool`
        Whether the logged in bot is added to this user's attachment menu.  
    is_premium: :class:`bool`
        Whether the user is subscribed to Telegram Premium.
    """

    @property
    def _chat_id(self) -> int:
        return self.id

    @property
    def _http_client(self) -> HTTPClient:
        return self._http


class ClientUser(BaseUser):
    """Represents your Telegram user.

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
        Whether the user is a bot.
    first_name: :class:`str`
        The first name of the user, if exists.
    last_name: :class:`str` | None
        The last name of the user, if exists.
    username: :class:`str` | None
        The username of the user, if applicable.
    language_code: :class:`str` | None
        The IETF language tag for the user's language, if applicable.
    added_to_attachment_menu: :class:`bool`
        Whether the logged in bot is added to this user's attachment menu.  
    is_premium: :class:`bool`
        Whether the user is subscribed to Telegram Premium.
    can_join_groups: :class:`bool`
        Whether the logged in bot can join groups.
    can_read_all_group_messages: :class:`bool`
        Whether privacy mode is disabled for the logged in bot.
    supports_inline_queries: :class:`bool`
        Whether the logged in bot has inline queries enabled.
    can_connect_to_business: :class:`bool`
        Whether the logged in bot can be connected to a Telegram business account to receive its messages.
    has_main_web_app: :class:`bool`
        Whether the logged in bot has a main web app.
    """

    def __init__(self, http: HTTPClient, data: UserPayload) -> None:
        super().__init__(http, data)
        self.can_join_groups: bool = data.get("can_join_groups", False)
        self.can_read_all_group_messages: bool = data.get("can_read_all_group_messages", False)
        self.supports_inline_queries: bool = data.get("supports_inline_queries", False)
        self.can_connect_to_business: bool = data.get("can_connect_to_business", False)
        self.has_main_web_app: bool = data.get("has_main_web_app", False)


class UserProfilePhotos:
    """Represents a collection of profile photos that belong to a user.

    Attributes
    ----------
    total_count: :class:`int`
        The total amount of profile photos the user has.
    photos: list[list[:class:`.PhotoSize`]]
        The photos that belong to the user. Each contained list contains one photo in up to four varying sizes.
    """

    def __init__(self, http: HTTPClient, data: UserProfilePhotosPayload) -> None:
        self._http: HTTPClient = http
        self.total_count: int = data["total_count"]
        self.photos: list[list[PhotoSize]] = [[PhotoSize(http, photo) for photo in photos] for photos in data["photos"]]
