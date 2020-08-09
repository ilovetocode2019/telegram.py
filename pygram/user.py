class User:
    """
    Represents a Telegram user

    Attributes
    ----------
    id: :class:`int`
        The ID of the user
    is_bot: :class:`bool`
        If the user is a bot
    username: Optional[:class:`str`]
        The username of the user
    first_name: :class:`str`
        The first name of the user
    last_name: Optional[:class:`str`]
        The last name of the user
    """

    def __init__(self, http, data):
        self._data = data
        self._http = http
        
        self.id = data.get("id")
        self.is_bot = data.get("is_bot")
        self.username = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")

    @property
    def full_name(self):
        """
        :class:`str`:
             The user's full name
        """

        return f"{self.first_name or ''} {self.last_name or ''}"

    @property
    def name(self):
        """
        :class:`int`:
            Username if the user has one. Otherwise the full name of the user.
        """

        return self.username or self.full_name

    async def send(self, content: str, parse_mode: str=None):
        """
        Sends a message directly to the user

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send
        
        Returns
        -------
        :class:`pygram.Message`
            The messsage sent

        Raises
        ------
        :exc:`pygram.HTTPException`
            Sending the message failed
        """

        return await self._http.send_message(chat_id=self.id, content=content, parse_mode="HTML")