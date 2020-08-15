class TelegramObject:
    """Base telegram object"""

    def __init__(self, http, data):
        self._http = http
        self._data = data

        self.id = data.get("id")

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id  == other.id

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True
