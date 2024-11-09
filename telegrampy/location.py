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

from typing import TYPE_CHECKING, Optional

from .abc import TelegramObject

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.location import Location as LocationPayload


class Location(TelegramObject):
    """Represents a point on the map.

    Attributes
    ----------
    latitude: :class:`float`
        The latitude defined by the sender.
    longitude: :class:`float`
        The longitude defined by the sender.
    horizontal_accuracy: Optional[:class:`float`]
        The radius of uncertanity for the point. This is measured in meters, ranging from 0 to 1500.
    live_period: Optional[:class:`int`]
        The amount of seconds after the message sending date, in which the location can still be updated.
    heading: Optional[:class:`int`]
        The direction the user is travelling in degrees.
        Only available for live locations.
    proximity_alert_radius: Optional[:class:`int`]
        The maximum distance for proximity alerts about approching another chat member.
        Only available for live locations.
    """

    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float]
    live_period: Optional[int]
    heading: Optional[int]
    proximity_alert_radius: Optional[int]

    def __init__(self, http: HTTPClient, data: LocationPayload):
        super().__init__(http)

        self.latitude: float = data.get("latitude")
        self.longitude: float = data.get("longitude")
        self.horizontal_accuracy: Optional[float] = data.get("horizontal_accuracy")
        self.live_period: Optional[int] = data.get("live_period")
        self.heading: Optional[int] = data.get("heading")
        self.proximity_alert_radius: Optional[int] = data.get("proximity_alert_radius")
