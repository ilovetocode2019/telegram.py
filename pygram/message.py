import datetime

from .chat import Chat
from .user import User


class Message:
    """
    Reprsents a message in Telegram

    Attributes
    ----------
    id: :class:`int`
        The ID of the message
    created_at: :class:`datetime.datetime`
        The time the message was created
    edited_at: Optional[:class:`datetime.datetime`]
        The time the message was edited
    content: :class:`str`
        The content of the message
    chat: :class:`pygram.Chat`
        The chat the message is in
    author: :class:`pygram.User`
        The author of the message
    """

    def __init__(self, http, data: dict):
        self._data = data
        self._http = http

        self.id = data.get("message_id")

        self.created_at = data.get("date")
        if self.created_at:
            datetime.datetime.fromtimestamp(self.created_at)

        self.edited_at = data.get("edit_date")
        if self.edited_at:
            datetime.datetime.fromtimestamp(self.edited_at)

        self.content = data.get("text")

        if "chat" in data:
            self.chat = Chat(http, data.get("chat"))
        else:
            self.chat = None

        if "from" in data:
            self.author = User(http, data.get("from"))
        else:
            self.author = None

    async def reply(self, content: str, parse_mode: str = None):
        """
        Replys to the message

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send
        parse_mode: :class:`str`
            The parse mode of the message to send

        Returns
        -------
        :class:`pygram.Message`
            The message sent

        Raises
        ------
        :exc:`pygram.HTTPException`
            Sending the message failed
        """

        return await self._http.send_message(chat_id=self.chat.id, content=content, parse_mode=parse_mode, reply_message_id=self.id)
