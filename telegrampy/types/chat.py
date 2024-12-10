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

from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

if TYPE_CHECKING:
    from .message import Message, Location
    from .user import User


class ChatPhoto(TypedDict):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_fild_unique_id: str


class ChatPermissions(TypedDict):
    can_send_messages: NotRequired[bool]
    can_send_media_messages: NotRequired[bool]
    can_send_polls: NotRequired[bool]
    can_send_other_messages: NotRequired[bool]
    can_add_web_page_previews: NotRequired[bool]
    can_change_info: NotRequired[bool]
    can_invite_users: NotRequired[bool]
    can_pin_messages: NotRequired[bool]
    can_send_other_messages: NotRequired[bool]


class ChatLocation(TypedDict):
    location: Location
    address: str


class Chat(TypedDict):
    id: int
    type: str
    title: NotRequired[str]
    username: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    photo: NotRequired[ChatPhoto]
    bio: NotRequired[str]
    has_private_forwards: NotRequired[Literal[True]]
    description: NotRequired[str]
    invite_link: NotRequired[str]
    pinned_message: NotRequired[Message]
    permissions: NotRequired[ChatPermissions]
    slow_mode_delay: NotRequired[int]
    message_auto_delete_time: NotRequired[int]
    has_protected_content: NotRequired[Literal[True]]
    sticker_set_name: NotRequired[str]
    can_set_sticker_set: NotRequired[Literal[True]]
    linked_chat_id: NotRequired[int]
    location: NotRequired[ChatLocation]


class ChatInviteLink(TypedDict):
    invite_link: str
    creator: User
    creates_join_request: NotRequired[bool]
    is_primary: NotRequired[bool]
    is_revoked: NotRequired[bool]
    name: NotRequired[str]
    expire_date: NotRequired[int]
    member_limit: NotRequired[int]
    pending_join_request_count: NotRequired[int]
    subscription_period: NotRequired[int]
    subscription_price: NotRequired[int]
