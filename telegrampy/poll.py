"""
MIT License

Copyright (c) 2020-2021 ilovetocode

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

from typing import List, TYPE_CHECKING

from .user import User
from .abc import TelegramObject

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.poll import (
        PollOption as PollOptionPayload,
        Poll as PollPayload,
        PollAnswer as PollAnswerPayload
    )


class Poll(TelegramObject):
    """A Telegram poll.

    .. container:: operations

        .. describe:: x == y

            Checks if two polls are equal.

        .. describe:: x != y

            Checks if two polls are not equal.

        .. describe:: str(x)

            Returns the poll's question.

    Attributes
    ----------
    id: :class:`int`
        The ID of the poll.
    question: :class:`str`
        The question of the poll.
    options: :class:`list`
        The options of the poll.
    total_voter_count: :class:`int`
        The total voter count of the poll.
    is_closed: :class:`bool`
        If the poll is closed.
    is_anonymous: :class:`bool`
        If the poll is anonymous.
    type: :class:`str`
        The type of the poll.
    allow_multiple_answers: :class:`bool`
        If the poll allows multiple answers.
    """

    if TYPE_CHECKING:
        question: str
        options: List[PollOptionPayload]
        total_voter_count: int
        is_closed: bool
        is_anonymous: bool
        type: str
        allows_multiple_answers: bool

    def __init__(self, http: HTTPClient, data: PollPayload) -> None:
        super().__init__(http)
        self.question: str = data.get("question")
        self.options: List[PollOptionPayload] = data.get("options")
        self.total_voter_count: int = data.get("total_voter_count")
        self.is_closed: bool = data.get("is_closed")
        self.is_anonymous: bool = data.get("is_anonymous")
        self.type: str = data.get("type")
        self.allows_multiple_answers: bool = data.get("allows_multiple_answers")

    def __str__(self) -> str:
        return self.question


class PollAnswer:
    """An answer to a non-anonymous poll.

    Attributes
    ----------
    poll_id: :class:`int`
        The ID of the poll.
    user: :class:`telegrampy.User`
        The user that answered the poll.
    option_ids: List[:class:`int`]
        The options that the user selected.
    """

    if TYPE_CHECKING:
        id: str
        user: User
        option_ids: List[int]

    def __init__(self, http: HTTPClient, data: PollAnswerPayload) -> None:
        self._data = data

        self.id: str = data.get("poll_id")
        self.user: User = User(http, data.get("user"))
        self.option_ids: List[int] = data.get("option_ids")
