"""
MIT License

Copyright (c) 2020 ilovetocode

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

import asyncio
import typing

import telegrampy


class NotStarted(telegrampy.TelegramException):
    """
    Raised when a conversation-specific method is called
    and the conversation has not been started.
    """
    def __init__(self):
        super().__init__("The conversation has not been started.")


class Question:
    """Represents a question the bot will ask the user

    Parameters
    ----------
    text: :class:`str`
        The question to ask the user
    """
    def __init__(self, func: typing.Callable, text: str, **kwargs):
        self.callback = func
        self.text = text

        self.starting_question = kwargs.pop("starting_question", False)

    async def __call__(self, conversation, message):
        await self.callback(conversation, message)


def question(text: str, **kwargs):
    """Turn a function into a conversation Question.

    For more info, see :class:`telegrampy.ext.conversations.Question`
    """

    def deco(func):
        return Question(func, text, **kwargs)

    return deco


class _ConversationMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        questions = []
        starting_question = None

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                if isinstance(value, Question):
                    questions.append(value)
                    if value.starting_question:
                        if starting_question is not None:
                            raise TypeError("More than one starting Question provided. "
                                            "There can only be one starting question.")
                        starting_question = value

        new_cls.__questions__ = questions
        new_cls.__starting_question__ = starting_question

        return new_cls


class Conversation(metaclass=_ConversationMeta):
    """Represents a conversation with another user in Telegram

    Parameters
    ----------
    abort_command :class:`str`
        The name of the command that will stop the conversation
    timeout: Optional[:class:`int`]
        How long to wait before the conversation times out.
        Defaults to None.
    """
    def __init__(self, *, abort_command: str, timeout: bool = None):
        if not self.__starting_question__:
            raise TypeError("No starting Question found. "
                            "Please specify a starting question through "
                            "the 'starting_question' kwarg in Question.")

        self.abort_command = abort_command
        self.timeout = timeout

        self.started = False  # when start() is run
        self.stopped = False  # when stop() is run

    async def start(self, message: telegrampy.Message, *, client: telegrampy.Client):
        """
        Start the conversation

        Parameters
        ----------
        message: :class:`telegrampy.Message`
            The message that invoked the conversation
        client: :class:`telegrampy.Client`
            The :class:`telegrampy.Client` instance to use
        """
        self.message = message
        self.chat = message.chat
        self.user = message.author
        self.client = client
        self.started = True

        await self.ask(self.__starting_question__)

    async def ask(self, question: Question, *, send_question: bool = True):
        """|coro|

        Ask a question.

        Parameters
        ----------
        question: :class:`.Question`
            The :class:`.Question` to ask
        send_question Optional[:class:`bool`]
            Whether to send the question's text before waiting for a response.
            Defaults to ``True``.

        Raises
        ------
        :exc:`.NotStarted`:
            The conversation hasn't been started
        :exc:`ValueError`:
            The question provided is not registered to the conversation
        """
        if not self.started:
            raise NotStarted()

        if question in self.__questions__:
            await self.chat.send(question.text)

            def check(ms):
                return ms.chat == self.chat and ms.author == self.user

            try:
                message = await self.client.wait_for("message", check=check, timeout=self.timeout)
            except asyncio.TimeoutError:
                await self.timed_out()
                return

            if message.content.startswith(f"/{self.abort_command}"):
                await self.abort(message)

            await question(self, message)

        else:
            raise ValueError("The method provided is not a registered Question.")

    async def stop(self):
        """|coro|

        Stop the conversation.
        """
        self.stopped = True

    async def abort(self, message):
        """|coro|

        Called when the abort command is used during a conversation.
        """
        await self.ctx.send("Aborted.")
        await self.stop()

    async def timed_out(self):
        """|coro|

        Called when the conversation times out.
        """
        await self.ctx.send("You timed out.")
        await self.stop()
