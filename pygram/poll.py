class Poll:
    """A telegram poll

    Attributes
    ----------
    question: :class:`str`
        The question of the poll
    options: :class:`list`
        The options of the poll
    total_voter_count: :class:`int`
        The total voter count of the poll
    is_closed: :class:`bool`
        If the poll is closed
    is_anonymous: :class:`bool`
        If the poll is anonymous
    type: :class:`str`
        The type of the poll
    allow_multiple_answers: :class:`bool`
        If the poll allows multiple answers
    """

    def __init__(self, data):
        self._data = data

        self.id = data.get("id")

        self.question = data.get("question")
        self.options = data.get("options")
        self.total_voter_count = data.get("total_voter_count")
        self.is_closed = data.get("is_closed")
        self.is_anonymous = data.get("is_anoymous")
        self.type = data.get("type")
        self.allow_multiple_answers = data.get("allow_multiple_answers")
