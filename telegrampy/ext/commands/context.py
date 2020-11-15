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

from telegrampy import File


class Context:
    """
    Context for a command.

    Attributes
    ----------
    bot: :class:`telegrampy.ext.commands.Bot`
        The bot that created the context.
    message: :class:`telegrampy.Message`
        The message the context is for.
    chat: :class:`telegrampy.Chat`
        The chat the context is for.
    author: :class:`telegrampy.User`
        The author of the message.
    command_failed: :class:`bool`
        Whether the command failed or not.
    args: :class:`list`
        The arguments passed into the command.
    kwargs: :class:`dict`
        The kwargs passed into the command.
    """

    def __init__(self, command, **kwargs):
        self.command = command
        self.bot = kwargs.get("bot")

        self.message = kwargs.get("message")
        self.chat = kwargs.get("chat")
        self.author = kwargs.get("author")
        self.command_failed = None
        self.args = kwargs.get("args") or []
        self.kwargs = kwargs.get("kwargs") or {}

    async def send(self, content: str = None, file: File = None, parse_mode=None):
        """|coro|
        
        Sends a message in the chat.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        file: :class:`telegrampy.File`
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

        return await self.chat.send(content=content, file=file, parse_mode=parse_mode)

    async def send_poll(self, question: str, options: list):
        """|coro|

        Sends a poll to the chat.

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

        Sends an action to the chat.

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
