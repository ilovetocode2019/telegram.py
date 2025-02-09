
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
from typing import TYPE_CHECKING

from .chat import PartialChat, Chat, ChatInvite
from .user import User

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.member import Member as MemberPayload
    from .types.member import MemberUpdated as MemberUpdatedPayload


class Member(User):
    """Represents a chat member, a superset of :class:`telegrampy.User` containing chat-specific details.

    Attributes
    ----------
    status: :class:`str`
        The status or role of the user in the chat.
    chat: :class:`telegrampy.PartialChat` | :class:`telegrampy.Chat`
        The chat that the user belongs to.
    id: :class:`int`
        The ID of the user.
    is_bot: :class:`bool`
        If the user is a bot.
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

    def __init__(self, http: HTTPClient, data: MemberPayload, *, chat: PartialChat) -> None:
        super().__init__(http, data["user"])
        self.status: str = data.get("status")
        self.chat: PartialChat = chat


class MemberUpdated:
    """Contains information about any change regarding a chat member.

    Attributes
    ----------
    chat: :class:`telegrampy.Chat`
        The chat that the update occured in.
    author: :class:`telegrampy.User`
        The user who performed the action resulting in a change.
    taken_at: :class:`datetime.datetime`
        The time that the action was taken at.
    old_member: :class:`telegrampy.Member`
        The affected chat member, prior to the change.
    new_member: :class:`telegrampy.Member`
        The affected chat member, after the change.
    invite_link: :class:`ChatInviteLink` | None
        The invite link used to join the chat, if applicable.
    via_join_request: :class:`bool`
        Whether the user joined the chat with a direct join request.
    via_chat_folder_invite_link: :class:`bool`
        Whether the the user joined the chat with a chat folder invite link.
    """

    def __init__(self, http: HTTPClient, data: MemberUpdatedPayload) -> None:
        self._http: HTTPClient = http

        self.chat: Chat = Chat(http, data["chat"])
        self.author: User = User(http, data["from"])

        self.taken_at: datetime.datetime = datetime.datetime.fromtimestamp(
            data["date"],
            tz=datetime.timezone.utc
        )

        self.old_member: Member = Member(http, data["old_chat_member"], chat=self.chat)
        self.new_member: Member = Member(http, data["new_chat_member"], chat=self.chat)

        self.invite_link: ChatInvite | None = ChatInvite(
            http,
            data["chat_invite_link"]
        ) if "chat_invite_link" in data else None

        self.via_join_request: bool = data.get("via_join_request", False)
        self.via_chat_folder_link: bool = data.get("via_chat_folder_link", False)
