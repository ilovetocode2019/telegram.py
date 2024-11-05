from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from .abc import TelegramObject
from .chat import Chat
from .user import User

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.member import Member as MemberPayload
    from .types.member import MemberUpdated as MemberUpdatedPayload

class Member(User):
    """
    Attributes
    ----------
    status: :class:`str`
        The status or role of the user in the chat.
    chat: :class::`telegrampy.Chat`
        The chat that the user belongs to.
    """

    if TYPE_CHECKING:
        status: str
        chat: Chat

    def __init__(self, http: HTTPClient, data: MemberPayload, *, chat: Chat):
        super().__init__(http, data.get("user"))

        self.status: str = data.get("status")
        self.chat: Chat = chat


class MemberUpdated(TelegramObject):
    """
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
    invite_link: Optional[Any]
        The invite link used to join the chat, if applicable.
    via_join_request: :class:`bool`
        Whether the user joined the chat with a direct join request.
    via_chat_folder_invite_link: :class:`bool`
        Whether the the user joined the chat with a chat folder invite link.
    """

    if TYPE_CHECKING:
        chat: Chat
        author: User
        taken_at: datetime.datetime
        old_member: Member
        new_member: Member
        invite_link: Optional[str]
        via_join_request: bool
        via_chat_folder_invite_link: bool

    def __init__(self, http: HTTPClient, data: MemberUpdatedPayload):
        super().__init__(http)

        self.chat: Chat = Chat(http, data.get("chat"))
        self.author: User = User(http, data.get("from"))
        self.taken_at: datetime.datetime = datetime.datetime.fromtimestamp(data.get("date"))
        self.old_member: Member = Member(http, data.get("old_chat_member"), chat=self.chat)
        self.new_member: Member = Member(http, data.get("new_chat_member"), chat=self.chat)
        self.invite_link: Optional[str] = None  # TODO
        self.via_join_request: bool = data.get("via_join_request", False)
        self.via_chat_folder_link: bool =data.get("via_chat_folder_link", False)
