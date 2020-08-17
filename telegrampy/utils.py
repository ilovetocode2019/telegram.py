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

import re


def escape_markdown(text: str, *, version: int = 2):
    """Tool that escapes markdown from a given string.

    Parameters
    ----------
    text: :class:`str`
        The text to escape markdown from.
    version: Optional[:class:`int`]
        The Telegram markdown version to use. Only 1 and 2 are supported.

    Returns
    -------
    :class:`str`
        The escaped text.

    Raises
    ------
    :exc:`ValueError`
        An unsupported version was provided.
    """
    if version == 1:
        characters = r"_*`["

    elif version == 2:
        characters = r"_*[]()~`>#+-=|{}.!"

    else:
        raise ValueError(f"Version '{version}' unsupported. Only version 1 and 2 are supported.")

    return re.sub(f"([{re.escape(characters)}])", r"\\\1", text)
