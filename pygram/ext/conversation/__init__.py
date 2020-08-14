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

import typing

import pygram


class NotStarted(pygram.TelegramException):
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

        self.starting_question = self.kwargs.pop("starting_question", False)

    def __call__(self, conversation, message):
        await self.callback(conversation, message)


class _ConversationMeta(type):
    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        questions = {}

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        new_cls.__starting_question__ = None

        # Attempt to find all Question methods and add them to the class
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                if isinstance(value, Question):
                    if value.starting_question:
                        new_cls.__starting_question__ = value
                    questions.append(value)

        new_cls.__questions__ = questions

        return new_cls


class Conversation(metaclass=_ConversationMeta):
    """Represents a conversation with another user in Telegram

    Parameters
    ----------
    timeout: :class:`int`
        How long to wait before the conversation times out.
        Defaults to None.
    """
    def __init__(self, *, timeout: bool = None):
        self.timeout = timeout

        self.started = False  # when start() is run
        self.stopped = False  # when stop() is run

    async def start(self, message: pygram.Message, *, client: pygram.Client):
        """
        Start the conversation

        Parameters
        ----------
        message: :class:`pygram.Message`
            The message that invoked the conversation
        client: :class:`pygram.Client`
            The :class:`pygram.Client` instance to use
        """
        self.started = True
        self.message = message
        self.chat = message.chat
        self.user = message.author
        self.bot = client

        await self.ask_question(self.__starting_question__)

    async def ask_question(self, question: Question):
        """Ask a question

        Parameters
        ----------
        question: :class:`.Question`
            The :class:`.Question` to ask

        Raises
        ------
        :exc:`.NotStarted`:
            The conversation hasn't been started
        :exc:`TypeError`:
            The question provided is not registered to the conversation
        """
        if not self.started:
            raise NotStarted()

        if question in self.__questions__:
            await self.chat.send(question.text)

            def check(ms):
                return ms.chat == self.chat and ms.author == self.user

            message = await self.client.wait_for("message", check=check, timeout=self.timeout)

            await question(self, message)

        else:
            raise TypeError("Not a registered Question.")

    async def stop(self):
        """Stop the conversation"""
        self.stopped = True


def question(text: str, **kwargs):
    """Turn a function into a conversation Question

    For more info, see :class:`pygram.ext.conversation.Question`
    """

    def deco(func):
        question = Question(func, text, **kwargs)
        return question

    return deco
