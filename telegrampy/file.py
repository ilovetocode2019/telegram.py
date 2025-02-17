"""
MIT License

Copyright (c) 2020-2024 ilovetocode

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

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from .errors import ClientException

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.file import File as FilePayload, PhotoSize as PhotoSizePayload


class File:
    """Represents basic information about a uploaded file.
 
    Attributes
    ----------
    id: :class:`str`
        Identifier of the file, which is useful for downloading or reusing it.
    unique_id: :class:`str`
        The globally unique identifier of the file, which is supposed to be permanent.
        This cannot be used for downloading or resuing the file.
    size: :class:`int` | None
        The size of the file's content in bytes.
    path: :class:`str` | None
        The relative path of the file on the server.
        In local mode, this is the absolute path on the filesystem, which may contain sensitive information such as the bot's token.
        The path is guaranteed to be valid for at least an hour.
        It is preferable to use :meth:`.read` or :meth:`.save` rather than using this directly.
    """
 
    def __init__(self, http: HTTPClient, data: FilePayload) -> None:
        self._http: HTTPClient = http
        self.id: str = data["file_id"]
        self.unique_id: str = data["file_unique_id"]
        self.size: int | None = data.get("file_size")
        self.path: str | None = data.get("file_path")

    async def refresh(self) -> File:
        """|coro|

        Creates a new file with an updated path.

        Returns
        -------
            The refreshed file.

        Raises
        ------
        HTTPException
            Fetching the updated file failed.
        """

        result = await self._http.get_file(file_id=self.id)
        return File(self._http, result)

    async def read(self) -> bytes:
        """|coro|

        Retrieves the contenst of the file.

        Returns
        -------
        :class:`bytes`
            The content of the file.

        Raises
        ------
        HTTPException
            Fetching the content of the file failed.
        ClientException
            The file has an absolute path to the local filesystem or none was provided.
        """

        if self.path is None:
            raise ClientException("No path provided for this file.")

        return await self._http.fetch_file(file_path=self.path)

    async def save(self, fp: str | io.BytesIO, *, seek_begin: bool = True) -> int:
        """|coro|

        Writes the content of the file to the disk or a file-like object.

        Parameters
        ----------
        fp: :class:`str` | :class:`io.BytesIO`
            The file-like object to write the content to or a filename to use.
        seek_being: :class:`bool`
            Whether to seek the beginning of the bytes-like object passed, after writing to it.

        Returns
        -------
        :class:`int`
            The length of the content written, in bytes.

        Raises
        ------
        HTTPException
            Fetching the content of the file failed.
        RuntimeError
            The file has no download path associated with it.
        """

        content = await self.read()

        if isinstance(fp, io.BytesIO):
            written = fp.write(content)
            if seek_begin:
                fp.seek(0)
            return written

        with open(fp, "wb") as f:
            return f.write(content)


class PhotoSize:
    """Represents a photo of a specific size. Also used for thumbnails of files and stickers.

    Attributes
    ----------
    file_id: :class:`str`
        Identifier of the file, which is useful for downloading or reusing it.
    file_unique_id: :class:`str`
        The globally unique identifier of the file, which is supposed to be permanent.
        This cannot be used for downloading or resuing the file.
    width: :class:`int`
        The width of the photo.
    height: :class:`int`
        The height of the photo.
    file_size: :class:`int` | None
        The size of the file's content in bytes.
    """

    def __init__(self, http: HTTPClient, data: PhotoSizePayload) -> None:
        self._http: HTTPClient = http
        self.file_id: str = data["file_id"]
        self.file_unique_id: str = data["file_unique_id"]
        self.width: int = data["width"]
        self.height: int = data["height"]
        self.file_size: int | None = data.get("file_size")

    async def get_file(self) -> File:
        """|coro|

        Fetches the file associated with the photo, whiches basic information and allows for downloading.

        Returns
        -------
        :class:`.File`
            The associated file.

        Raises
        ------
        HTTPException
            Fetching the associated file failed.
        """

        result = await self._http.get_file(file_id=self.file_id)
        return File(self._http, result)
