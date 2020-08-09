from .file import File

class Context:
    """
    Context for a command

    Attributes
    ----------
    bot: :class:`pygram.Bot`
        The bot that created the context
    message: :class:`pygram.Message`
        The message the context is for
    chat: :class:`pygram.Chat`
        The chat the context is for
    author: :class:`pygram.User`
        The author of the message
    args: :class:`list`
        The arguments passed into the command
    kwargs: :class:`dict`
        The kwargs passed into the command
    """

    def __init__(self, command, **kwargs):
        self.command = command
        self.bot = kwargs.get("bot")

        self.message = kwargs.get("message")
        self.chat = kwargs.get("chat")
        self.author = kwargs.get("author")
        self.args = kwargs.get("args") or []
        self.kwargs = kwargs.get("kwargs") or {}

    async def send(self, content: str=None, file: File=None, parse_mode=None):
        """
        Sends a message in the chat

        Parameters
        ----------
        content: :class:`str`
            The content of the message to send
        file: :class:`pygram.File`
            The file to send
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

        return await self.chat.send(content=content, file=file, parse_mode=parse_mode)

    async def send_poll(self, question: str, options: list):
        """
        Sends a poll to the chat

        Parameters
        ----------
        question: :class:`str`
            The question of the poll
        options: List[:class:`str`]
            The options in the poll

        Returns
        -------
        :class:`pygram.Poll`
            The poll sent

        Raises
        ------
        :exc:`pygram.HTTPException`
            Sending the poll failed
        """

        return await self.chat.send_poll(question, options)

    async def send_action(self, action: str):
        """
        Sends an action to the chat

        Parameters
        ----------
        action: :class:`str`
            The action to send

        Raises
        ------
        :exc:`pygram.HTTPException`
            Sending the action failed
        """

        await self.chat.send_action(action)

    async def reply(self, content: str, parse_mode: str=None):
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

        return await self.message.reply(content=content, parse_mode=parse_mode)