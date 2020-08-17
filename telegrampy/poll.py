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

class Poll:
    """A telegram poll.

    Attributes
    ----------
    question: :class:`str`
        The question of the poll.
    options: :class:`list`
        The options of the poll.
    total_voter_count: :class:`int`
        The total voter count of the poll.
    is_closed: :class:`bool`
        If the poll is closed.
    is_anonymous: :class:`bool`
        If the poll is anonymous.
    type: :class:`str`
        The type of the poll.
    allow_multiple_answers: :class:`bool`
        If the poll allows multiple answers.
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
