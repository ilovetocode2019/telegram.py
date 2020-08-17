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

from .file import *
from .abc import TelegramObject


class User(TelegramObject):
    """
    Represents a Telegram user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: str(x)

            Returns the user's name.

    Attributes
    ----------
    id: :class:`int`
        The ID of the user.
    is_bot: :class:`bool`
        If the user is a bot.
    username: Optional[:class:`str`]
        The username of the user.
    first_name: :class:`str`
        The first name of the user.
    last_name: Optional[:class:`str`]
        The last name of the user.
    """

    def __init__(self, http, data):
        super().__init__(http, data)
        self.is_bot = data.get("is_bot")
        self.username = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """
        :class:`str`:
             The user's full name.
        """

        return f"{self.first_name or ''} {self.last_name or ''}"

    @property
    def name(self):
        """
        :class:`str`:
            Username if the user has one. Otherwise the full name of the user.
        """

        return self.username or self.full_name

    async def send(self, content: str = None, file: File = None, parse_mode: str = None):
        """|coro|
        
        Sends a message directly to the user.

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send.
        file: :class:`telegrampy.File`
            The file to send
        parse_mode: :class:`str`
            The parse mode of the message to send.

        Returns
        -------
        :class:`telegrampy.Message`
            The message sent.

        Raises
        ------
        :exc:`errors.HTTPException`
            Sending the message failed.
        """

        if not file:
            return await self._http.send_message(chat_id=self.id, content=content, parse_mode=parse_mode)
        else:
            if isinstance(file, Document):
                return await self._http.send_document(chat_id=self.id, document=file.file, filename=file.filename)

            elif isinstance(file, Photo):
                return await self._http.send_photo(chat_id=self.id, photo=file.file, filename=file.filename, caption=file.caption)
