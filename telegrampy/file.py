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

from io import BytesIO


class File:
    """A file to send."""

    def __init__(self, file: BytesIO, filename: str = None):
        self.file = file
        self.filename = filename


class Document(File):
    """
    A document to send.

    Attributes
    ----------
    file: :class:`io.BytesIO`
        The document.
    filename: Optional[:class:`str`]
        The filename of the document.

    Parameters
    ----------
    file: :class:`io.BytesIO`
        The document.
    filename: :class:`str`
        The filename of the document.
    """


class Photo(File):
    """
    A photo to send.

    Attributes
    ----------
    file: :class:`io.BytesIO`
        The photo.
    filename: Optional[:class:`str`]
        The filename of the photo.
    caption: Optional[:class:`str`]
        The caption of the photo.

    Parameters
    ----------
    file: :class:`io.BytesIO`
        The photo.
    filename: :class:`str`
        The filename of the photo.
    caption: :class:`str`
        The caption of the photo.
    """

    def __init__(self, file: BytesIO, filename: str = None, caption: str = None):
        super().__init__(file, filename)
        self.caption = caption
