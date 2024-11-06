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

from typing import TYPE_CHECKING, Any, List, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from .chat import Chat
    from .poll import Poll
    from .user import User


class MessageEntity(TypedDict):
    type: str
    offset: int
    length: int
    url: str
    user: User
    language: str
    custom_emoji_id: str


class _BaseFile(TypedDict):
    file_id: str
    file_unique_id: str
    file_size: Optional[int]

class PhotoSize(_BaseFile):
    width: int
    height: int


class _File(_BaseFile):
    thumb: Optional[PhotoSize]
    file_name: Optional[str]
    mime_type: Optional[str]


class Animation(_File):
    duration: int
    width: int
    height: int


class Audio(_File):
    duration: int
    performer: Optional[str]
    title: Optional[str]


Document = _File
Video = Animation


class VideoNote(_BaseFile):
    length: int
    duration: int
    thumb: Optional[PhotoSize]


class Voice(_BaseFile):
    duration: int
    thumb: Optional[PhotoSize]
    mime_type: Optional[str]


class Contact(TypedDict):
    phone_number: str
    first_name: str
    last_name: Optional[str]
    user_id: Optional[int]
    vcard: Optional[str]


class Dice(TypedDict):
    emoji: str
    value: int


class Location(TypedDict):
    longitude: float
    latitude: float
    horizontal_accuracy: Optional[float]
    live_period: Optional[int]
    heading: Optional[int]
    proximity_alert_radius: Optional[int]


class Venue(TypedDict):
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str]
    foursquare_type: Optional[str]
    google_place_id: Optional[str]
    google_place_type: Optional[str]


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
    users: Optional[List[User]]


class UserProfilePhotos(TypedDict):
    total_count: int
    photos: List[PhotoSize]


class File(_BaseFile):
    file_path: Optional[str]

# If there's a better way to include the "from" key, please let me know
Message = TypedDict(
    "Message",
    {
        "message_id": int,
        "from": Optional[User],
        "sender_chat": Optional[Chat],
        "date": int,
        "chat": Chat,
        "forward_from": Optional[Chat],
        "forward_from_chat": Optional[int],
        "forward_date": Optional[int],
        "is_automatic_forward": Optional[Literal[True]],
        "reply_to_message": Optional["Message"],
        "via_bot": Optional[User],
        "edit_date": Optional[int],
        "has_protected_content": Optional[Literal[True]],
        "media_group_id": Optional[str],
        "author_signature": Optional[str],
        "text": Optional[str],
        "entities": Optional[List[MessageEntity]],
        "animation": Optional[Animation] ,
        "audio": Optional[Audio],
        "document": Optional[Document],
        "photo": Optional[List[PhotoSize]],
        "sticker": Optional[Any],  # TODO
        "video": Optional[Video],
        "video_note": Optional[VideoNote],
        "voice": Optional[Voice],
        "caption": Optional[str],
        "caption_entities": Optional[List[MessageEntity]],
        "contact": Optional[Contact],
        "dice": Optional[Dice],
        "game": Optional[Any],  # TODO
        "poll": Optional[Poll],
        "venue": Optional[Venue],
        "new_chat_members": Optional[List[User]],
        "left_chat_member": Optional[User],
        "new_chat_title": Optional[str],
        "new_chat_photo": Optional[List[PhotoSize]],
        "delete_chat_photo": Optional[Literal[True]],
        "group_chat_created": Optional[Literal[True]],
        "supergroup_chat_created": Optional[Literal[True]],
        "channel_chat_created": Optional[Literal[True]],
        "message_auto_delete_timer_changed": Optional[MessageAutoDeleteTimerChanged],
        "migrate_to_chat_id": Optional[int],
        "migrate_from_chat_id": Optional[int],
        "pinned_message": Optional["Message"],
        "invoice": Optional[Any],  # TODO
        "successful_payment": Optional[Any],  # TODO
        "connected_website": Optional[str],
        "passport_data": Optional[Any],  # TODO
        "proximity_alert_triggered": Optional[ProximityAlertTriggered],
        "voice_chat_scheduled": Optional[VoiceChatScheduled],
        "voice_chat_started": Optional[VoiceChatStarted],
        "voice_chat_ended": Optional[VoiceChatEnded],
        "voice_chat_participants_invited": Optional[VoiceChatParticipantsInvited],
        "reply_markup": Optional[Any],  # TODO
    }
)
