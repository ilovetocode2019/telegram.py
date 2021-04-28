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

import io
import typing


class Context:
    """
    Context for a command.

    Attributes
    ----------
    bot: :class:`telegrampy.ext.commands.Bot`
        The bot that created the context.
    message: :class:`telegrampy.Message`
        The message the invoked the command.
    command: :class:`telegrampy.Command`
        The command that is being invoked.
    invoked_with: :class:`str`
        The text that triggered the invocation.
    chat: :class:`telegrampy.Chat`
        The chat the command is being invoked in.
    author: :class:`telegrampy.User`
        The author invoking the command.
    command_failed: :class:`bool`
        If the command failed or not.
    args: :class:`list`
        The arguments passed into the command.
    kwargs: :class:`dict`
        The kwargs passed into the command.
    """

    def __init__(self, **kwargs):
        self.bot = kwargs.get("bot")
        self.message = kwargs.get("message")
        self.command = kwargs.get("command")
        self.invoked_with = kwargs.get("invoked_with")
        self.chat = kwargs.get("chat")
        self.author = kwargs.get("author")
        self.args = kwargs.get("args") or []
        self.kwargs = kwargs.get("kwargs") or {}
        self.command_failed = None

    async def send(self, content: str = None, parse_mode: str = None):
        """|coro|

        Sends a message to the destination.

        Parameters
        ----------
        content: :class:`str`
            The file to send.
        parse_mode: :class:`str`
            The parse mode of the message to send.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the message failed.
        """

        return await self.chat.send(content=content, parse_mode=parse_mode)

    async def send_document(self, document: typing.Union[io.BytesIO, str], filename: str = None, caption: str = None, parse_mode: str = None):
        """|coro|

        Sends a document to the destination.

        Parameters
        ----------
        document: Union[class:`io.BytesIO`, :class:`str`]
            The document to send. Either a file or the path to one.
        filename: :class:`str`
            The filename of the document.
        caption: :class:`str`
            The document's caption.
        parse_mode: :class:`str`
            The parse mode for the caption.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the document failed.
        """

        if isinstance(document, str):
            with open(document, "rb") as file:
                content = file.read()
                document = io.BytesIO(content)

        return await self.chat.send_document(document=document, filename=filename, caption=caption, parse_mode=parse_mode)

    async def send_photo(self, photo: typing.Union[io.BytesIO, str], filename: str = None, caption: str = None, parse_mode: str = None):
        """|coro|

        Sends a photo to the destination.

        Parameters
        ----------
        photo: Union[class:`io.BytesIO`, :class:`str`]
            The photo to send. Either a file or the path to one.
        filename: Optional[:class:`str`]
            The filename of the photo.
        caption: Optional[:class:`str`]
            The caption for the photo.
        parse_mode: Optional[:class:`str`]
            The parse mode for the caption.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the photo failed.
        """

        if isinstance(photo, str):
            with open(document, "rb") as file:
                content = file.read()
                document = io.BytesIO(content)

        return await self.chat.send_photo(photo=photo, filename=filename, caption=caption, parse_mode=parse_mode)

    async def send_poll(self, question: str, options: list):
        """|coro|

        Sends a poll to the destination.

        Parameters
        ----------
        question: :class:`str`
            The question of the poll.
        options: List[:class:`str`]
            The options in the poll.

        Returns
        -------
        :class:`telegrampy.Poll`
            The poll sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the poll failed.
        """

        return await self.chat.send_poll(question, options)

    async def send_action(self, action: str):
        """|coro|

        Sends an action to the destination.

        Parameters
        ----------
        action: :class:`str`
            The action to send.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the action failed.
        """

        await self.chat.send_action(action)

    def action(self, action: str):
        """
        Returns a context manager that sends a chat action, until the with statment is completed.

        Parameters
        ----------
        action: :class:`str`
            The action to send.
        """

        return self.chat.action(action)

    async def reply(self, content: str, parse_mode: str = None):
        """
        |coro|

        Replys to the message.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        parse_mode: :class:`str`
            The parse mode of the message to send.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Sending the message failed.
        """

        return await self.message.reply(content=content, parse_mode=parse_mode)
