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

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing_extensions import Self

    from telegrampy.chat import Chat
    from telegrampy.client import Client
    from telegrampy.message import Message
    from telegrampy.user import User

    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    CoroFunc = Callable[..., Coro[Any]]
    QuestionCallbackType = Callable[["Conversation", Message]]

class Question:
    """Represents a question the bot will ask the user.

    Parameters
    ----------
    func: :ref:`coroutine <coroutine>`
        The question's callback, taking two arguments:
        The :class:`Conversation` instance and the :class:`Message` that triggered the callback.
    text: :class:`str`
        The content to ask the user.
    starting_question: :class:`bool` | None
        Designates the question as the starting question.
        Defaults to ``False``.
    """
    def __init__(self, func: QuestionCallbackType, text: str, *, starting_question: bool = False) -> None:
        self.callback: QuestionCallbackType = func
        self.text: str = text
        self.starting_question: bool = starting_question

    async def invoke(self, conversation: Conversation, message: Message) -> None:
        await self.callback(conversation, message)


def question(text: str, *, starting_question: bool = False) -> Callable[[CoroFunc], Question]:
    """Turn a function into a conversation :class:`.Question`.

    Parameters
    ----------
    text: :class:`str`
        The question to ask the user.
    starting_question: :class:`bool` | None
        Designates a Question as the starting question.
        Defaults to ``False``.
    """

    def deco(func: CoroFunc) -> Question:
        return Question(func, text, starting_question=starting_question)

    return deco


class Conversation:
    """Represents a conversation with another user in Telegram

    Parameters
    ----------
    chat: :class:`telegrampy.Chat`
        The chat that the conversation is taking place in.
    user: :class:`telegrampy.User`
        The user to listen to messages from.
    client: :class:`.Client`
        The client associated with the conversation.
    abort_command: :class:`str` | None
        The name of the command that will stop the conversation.
        Defaults to ``'abort'``.
    timeout: :class:`float` | None
        How long to wait before the conversation times out.
        Defaults to ``None``.
    """

    __questions__: ClassVar[list[Question]]
    __starting_question__: ClassVar[Question]

    def __init_subclass__(cls) -> None:
        questions = []
        starting_question = None

        for base in reversed(cls.__mro__):
            for elem, value in base.__dict__.items():
                if isinstance(value, Question):
                    questions.append(value)
                    if value.starting_question is True:
                        if starting_question is not None:
                            raise TypeError("Only one starting question is allowed.")
                        starting_question = value

        if starting_question is None:
            raise TypeError("No starting question specified.")

        cls.__questions__ = questions
        cls.__starting_question__ = starting_question

    def __init__(
        self,
        *,
        chat: Chat,
        user: User,
        client: Client,
        abort_command: str = "abort",
        timeout: float | None = None
    ) -> None:
        self.abort_command: str = abort_command
        self.timeout: float | None = timeout

        self.started: bool = False  # when start() is run
        self.stopped: bool = False  # when stop() is run
        self._event: asyncio.Event = asyncio.Event()

        self.chat: Chat = chat
        self.user: User = user
        self.client: Client = client

    @classmethod
    def from_message(
        cls,
        message: Message,
        *,
        client: Client,
        abort_command: str = "abort",
        timeout: float | None = None
    ) -> Self:
        """Constructs a new conversation from a a :class:`.Message`.

        Parameters
        ----------
        :class:`.Message`
            The message associated with the conversation.
        :class:`.Client`
            The client associated with the conversation.
        """

        if message.author is None:
            raise RuntimeError("Message has no author.")

        return cls(
            chat=message.chat,
            user=message.author,
            client=client,
            abort_command=abort_command,
            timeout=timeout
        )

    async def start(self, *, wait: bool = False) -> None:
        """
        Start the conversation

        Parameters
        ----------
        wait: :class:`bool` | None
            Whether to wait until the conversation is completed
            before returning.
        """

        self.started = True
        self.client.loop.create_task(self.ask(self.__starting_question__))

        if wait:
            await self._event.wait()

    async def ask(self, question: Question, *, send_question: bool = True) -> None:
        """|coro|

        Ask a question.

        Parameters
        ----------
        question: :class:`.Question`
            The :class:`.Question` to ask
        send_question: :class:`bool`
            Whether to send the question's text before waiting for a response.
            Defaults to ``True``.

        Raises
        ------
        :exc:`.RuntimeError`:
            The conversation hasn't been started
        :exc:`ValueError`:
            The question provided is not registered to the conversation
        """
        if not self.started:
            raise RuntimeError("This conversation has not been started.")

        if question in self.__questions__:
            await self.chat.send(question.text)

            def check(ms):
                return ms.chat == self.chat and ms.author == self.user

            try:
                message = await self.client.wait_for("message", check=check, timeout=self.timeout)
            except asyncio.TimeoutError:
                await self.timed_out()
                return self.stop()

            content = message.content
            base_cmd = f"/{self.abort_command}"

            if content == base_cmd or content.startswith(f"{base_cmd}@"):
                await self.abort(message)
                return self.stop()

            await question.invoke(self, message)

        else:
            raise ValueError("The method provided is not a registered Question.")

    def stop(self) -> None:
        """|coro|

        Stops the conversation.
        """

        self._event.set()
        self.stopped = True

    async def abort(self, message) -> None:
        """|coro|

        Called when the abort command is used during a conversation. Can be overriden by subclasses.
        """

        await self.chat.send("Aborted.")

    async def timed_out(self) -> None:
        """|coro|

        Called when the conversation times out. Can be overriden by subclasses.
        """

        await self.chat.send("You timed out.")
