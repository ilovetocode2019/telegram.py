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

from typing import TYPE_CHECKING, Any, List, Literal, NotRequired, TypedDict

if TYPE_CHECKING:
    from .chat import Chat
    from .poll import Poll
    from .user import User


class MessageEntity(TypedDict):
    type: str
    offset: int
    length: int
    url: NotRequired[str]
    user: NotRequired[User]
    language: NotRequired[str]
    custom_emoji_id: NotRequired[str]


class _BaseFile(TypedDict):
    file_id: str
    file_unique_id: str
    file_size: NotRequired[int]

class PhotoSize(_BaseFile):
    width: int
    height: int


class _File(_BaseFile):
    thumb: NotRequired[PhotoSize]
    file_name: NotRequired[str]
    mime_type: NotRequired[str]


class Animation(_File):
    duration: int
    width: int
    height: int


class Audio(_File):
    duration: int
    performer: NotRequired[str]
    title: NotRequired[str]


Document = _File
Video = Animation


class VideoNote(_BaseFile):
    length: int
    duration: int
    thumb: NotRequired[PhotoSize]


class Voice(_BaseFile):
    duration: int
    thumb: NotRequired[PhotoSize]
    mime_type: NotRequired[str]


class Contact(TypedDict):
    phone_number: str
    first_name: str
    last_name: NotRequired[str]
    user_id: NotRequired[int]
    vcard: NotRequired[str]


class Dice(TypedDict):
    emoji: str
    value: int


class Location(TypedDict):
    longitude: float
    latitude: float
    horizontal_accuracy: NotRequired[float]
    live_period: NotRequired[int]
    heading: NotRequired[int]
    proximity_alert_radius: NotRequired[int]


class Venue(TypedDict):
    location: Location
    title: str
    address: str
    foursquare_id: NotRequired[str]
    foursquare_type: NotRequired[str]
    google_place_id: NotRequired[str]
    google_place_type: NotRequired[str]


class ProximityAlertTriggered(TypedDict):
    traveler: User
    watcher: User
    distance: int


class MessageAutoDeleteTimerChanged(TypedDict):
    message_auto_delete_time: int


class VoiceChatScheduled(TypedDict):
    start_date: int


VoiceChatStarted = object


class VoiceChatEnded(TypedDict):
    duration: int


class VoiceChatParticipantsInvited(TypedDict):
    users: NotRequired[List[User]]


class UserProfilePhotos(TypedDict):
    total_count: int
    photos: List[PhotoSize]


class File(_BaseFile):
    file_path: NotRequired[str]


class InaccessibleMessage(TypedDict):
    chat: Chat
    message_id: int
    date: Literal[0]

Message = TypedDict(
    "Message",
    {
        "message_id": int,
        "from": NotRequired[User],
        "sender_chat": NotRequired[Chat],
        "date": int,
        "chat": Chat,
        "forward_from": NotRequired[Chat],
        "forward_from_chat": NotRequired[int],
        "forward_date": NotRequired[int],
        "is_automatic_forward": NotRequired[Literal[True]],
        "reply_to_message": NotRequired["Message"],
        "via_bot": NotRequired[User],
        "edit_date": NotRequired[int],
        "has_protected_content": NotRequired[Literal[True]],
        "media_group_id": NotRequired[str],
        "author_signature": NotRequired[str],
        "text": NotRequired[str],
        "entities": NotRequired[List[MessageEntity]],
        "animation": NotRequired[Animation] ,
        "audio": NotRequired[Audio],
        "document": NotRequired[Document],
        "photo": NotRequired[List[PhotoSize]],
        "sticker": NotRequired[Any],  # TODO
        "video": NotRequired[Video],
        "video_note": NotRequired[VideoNote],
        "voice": NotRequired[Voice],
        "caption": NotRequired[str],
        "caption_entities": NotRequired[List[MessageEntity]],
        "contact": NotRequired[Contact],
        "dice": NotRequired[Dice],
        "game": NotRequired[Any],  # TODO
        "poll": NotRequired[Poll],
        "venue": NotRequired[Venue],
        "new_chat_members": NotRequired[List[User]],
        "left_chat_member": NotRequired[User],
        "new_chat_title": NotRequired[str],
        "new_chat_photo": NotRequired[List[PhotoSize]],
        "delete_chat_photo": NotRequired[Literal[True]],
        "group_chat_created": NotRequired[Literal[True]],
        "supergroup_chat_created": NotRequired[Literal[True]],
        "channel_chat_created": NotRequired[Literal[True]],
        "message_auto_delete_timer_changed": NotRequired[MessageAutoDeleteTimerChanged],
        "migrate_to_chat_id": NotRequired[int],
        "migrate_from_chat_id": NotRequired[int],
        "pinned_message": NotRequired["Message"],
        "invoice": NotRequired[Any],  # TODO
        "successful_payment": NotRequired[Any],  # TODO
        "connected_website": NotRequired[str],
        "passport_data": NotRequired[Any],  # TODO
        "proximity_alert_triggered": NotRequired[ProximityAlertTriggered],
        "voice_chat_scheduled": NotRequired[VoiceChatScheduled],
        "voice_chat_started": NotRequired[VoiceChatStarted],
        "voice_chat_ended": NotRequired[VoiceChatEnded],
        "voice_chat_participants_invited": NotRequired[VoiceChatParticipantsInvited],
        "reply_markup": NotRequired[Any],  # TODO
    }
)
