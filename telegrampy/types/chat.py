"""
MIT License

Copyright (c) 2020-2021 ilovetocode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without reOptional[str]iction, including without limitation the rights
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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from .message import Message, Location


class ChatPhoto(TypedDict):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_fild_unique_id: str


class ChatPermissions(TypedDict):
    can_send_messages: Optional[bool]
    can_send_media_messages: Optional[bool]
    can_send_polls: Optional[bool]
    can_send_other_messages: Optional[bool]
    can_add_web_page_previews: Optional[bool]
    can_change_info: Optional[bool]
    can_invite_users: Optional[bool]
    can_pin_messages: Optional[bool]
    can_send_other_messages: Optional[bool]


class ChatLocation(TypedDict):
    location: Location
    address: str


class Chat(TypedDict):
    id: int
    type: str
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    photo: Optional[ChatPhoto]
    bio: Optional[str]
    has_private_forwards: Optional[Literal[True]]
    description: Optional[str]
    invite_link: Optional[str]
    pinned_message: Optional[Message]
    permissions: Optional[ChatPermissions]
    slow_mode_delay: Optional[int]
    message_auto_delete_time: Optional[int]
    has_protected_content: Optional[Literal[True]]
    sticker_set_name: Optional[str]
    can_set_sticker_set: Optional[Literal[True]]
    linked_chat_id: Optional[int]
    location: Optional[ChatLocation]
