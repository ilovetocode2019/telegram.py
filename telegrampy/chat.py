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
import io

from .abc import Messageable
from .mixins import Hashable

from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
)

if TYPE_CHECKING:
    from .http import HTTPClient
    from .member import Member
    from .message import PartialMessage
    from .user import User
    from .types.chat import Chat as ChatPayload, ChatInviteLink as ChatInviteLinkPayload


class PartialChat(Messageable, Hashable):
    """Represents a partial chat that can be interacted with, without containing information.

    .. container:: operations

        .. describe:: x == y

            Checks if two partial chats are equal.

        .. describe:: x != y

            Checks if two chats partial are not equal.

    Attributes
    ----------
    id: :class:`int`
        The given ID of the partial chat.
    """

    def __init__(self, http: HTTPClient, chat_id: int):
        self._http: HTTPClient = http
        self.id: int = chat_id

    @property
    def _chat_id(self) -> int:
        return self.id

    @property
    def _http_client(self) -> HTTPClient:
        return self._http

    def get_partial_message(self, message_id: int) -> PartialMessage:
        """Returns a partial message for the given ID, without fetching anything from Telegram.

        This is useful for interacting with the messages if you only have an ID.

        Returns
        -------
        :class:`telegrampy.PartialMessage`
            The partial message that can be interacted with.
        """

        from .message import PartialMessage
        return PartialMessage(self._http_client, message_id, chat=self)

    async def get_member(self, user_id: int) -> Member:
        """|coro|

        Fetches a member in the chat.

        Parameters
        ----------
        user_id: :class:`int`
            The user ID of the member.

        Returns
        -------
        :class:`telegrampy.Member`
            The member fetched.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Fetching the member failed.
        """

        from .member import Member
        result = await self._http.get_chat_member(chat_id=self.id, user_id=user_id)
        return Member(self._http, result, chat=self)

    async def set_photo(self, photo: Optional[Union[io.BytesIO, str]]) -> None:
        """|coro|

        Sets the photo for the chat. This does not work in private chats.

        Parameters
        ----------
        photo: Union[:class:`io.BytesIO`, :class:`str`]
            The new profile photo for the chat. Pass :class:`None` to clear.
        """

        if isinstance(photo, str):
            with open(photo, "rb") as file:
                content = file.read()
                photo = io.BytesIO(content)

        if photo:
            await self._http.set_chat_photo(chat_id=self.id, photo=photo)
        else:
            await self._http.delete_chat_photo(chat_id=self.id)

    async def set_title(self, title: str) -> None:
        """|coro|

        Changes the title of the chat.
        This only works in non-private chats with administrator privillages.

        Parameters
        ----------
        title: :class:`str`
            The new name of the chat, from 1 to 128 characaters.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Changing the title failed.
        """

        await self._http.set_chat_title(chat_id=self.id, title=title)

    async def set_description(self, description: Optional[str]) -> None:
        """|coro|

        Changes the description of the chat.
        This only works in non-private chats with administrator privillages.

        Parameters
        ----------
        description: :class:`str`
            The new description of the chat, up to 255 characters.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Changing the description failed.
        """

        await self._http.set_chat_description(chat_id=self.id, description=description)

    async def clear_pins(self) -> None:
        """|coro|

        Removes all pins from the chat. Must have administrator with proper permissions.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Clearing all pins failed.
        """

        await self._http.unpin_all_chat_messages(chat_id=self.id)

    async def leave(self) -> None:
        """|coro|

        Removes the logged in bot from a non-private chat.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Leaving the chat failed.
        """

        await self._http.leave_chat(chat_id=self.id)


class Chat(PartialChat):
    """Represents a chat in Telegram.

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
    type: :class:`str`
        The type of the chat. Can be "private", "group", "supergroup", or "channel".
    title: Optional[:class:`str`]
        The title of the chat, if applicable..
    username: Optional[:class:`str`]
        The username of the chat, if applicable.
    first_name: Optional[:class:`str`]
        The first name of the user, if applicable.
    last_name: Optional[:class:`str`]
        The last name of the user, if applicable.
    is_forum: :class:`bool`
        Whether the chat is set up as a forum.
    """

    def __init__(self, http: HTTPClient, data: ChatPayload):
        self._http: HTTPClient = http
        self.id: int = data["id"]
        self.type: str = data["type"]
        self.title: Optional[str] = data.get("title")
        self.username: Optional[str] = data.get("username")
        self.first_name: Optional[str] = data.get("first_name")
        self.last_name: Optional[str] = data.get("last_name")
        self.is_forum: bool = data.get("is_forum", False)

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        """:class:`str`: The display name of the chat, as it appears in the client."""

        if self.title:
            return self.title
        else:
            return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

class ChatInvite:
    """Represents an invite to a chat in the form of a link.

    Attributes
    ----------
    invite_link: :class:`str`
        The invite link.
    creator: :class:`telegrampy.User`
        The user who created the link
    creates_join_request: :class:`bool`
        Whether users joining the chat need to be approved by the administrators.
    is_primary: :class:`bool`
        Whether this is the primary link for the chat.
    is_revoked: :class:`bool`
        Whether the link has been revoked.
    name: Optional[:class:`bool`]
        The name of the invite link.
    expire_date: Optional[:class:`datetime.datetime`]
        The time that the link will expire or the time it expired at if it already has.
    member_limit: Optional[:class:`int`]
        The maxmimum number of users that can be simultaneous chat members, by joining through this link.
    pending_join_request_count: Optional[:class:`int`]
        The number of pending join requests for users of the link.
    subscription_period: Optional[class:`int`]
        The number of seconds the subscription will be active for before the next payment
    subscription_price: Optional[:class:`int`]
        The number of stars a chat member must pay initally and after each following subscription period.
    """

    def __init__(self, http: HTTPClient, data: ChatInviteLinkPayload):
        self._http: HTTPClient = http
        self.link: str = data["invite_link"]
        self.creator: User = User(http, data["creator"])
        self.creates_join_request: bool = data.get("creates_join_request", False)
        self.is_primary: bool = data.get("is_primary", False)
        self.is_revoked: bool = data.get("is_revoked", False)
        self.name: Optional[str] = data.get("name")
        self.expire_date: Optional[datetime.datetime] = (
            datetime.datetime.fromtimestamp(data["expire_date"], tz=datetime.timezone.utc)
            if "expire_date" in data
            else None
        )
        self.member_limit: Optional[int] = data.get("member_limit")
        self.pending_join_request_count: Optional[int] = data.get("pending_join_request_count")
        self.subscription_period: Optional[int] = data.get("subscription_period")
        self.subscription_price: Optional[int] = data.get("subscription_price")
