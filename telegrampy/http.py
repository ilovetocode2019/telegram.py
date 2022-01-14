"""
MIT License

Copyright (c) 2020-2021 ilovetocode

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

import asyncio
import io
import json
import logging
import sys
from typing import Any, TYPE_CHECKING, List, Literal, Sequence, TypeVar, Coroutine, Optional, Dict

import aiohttp

from . import __version__
from .errors import *
from .user import User
from .chat import Chat
from .message import Message
from .poll import Poll

if TYPE_CHECKING:
    T = TypeVar("T")
    Response = Coroutine[Any, Any, T]
    HTTPMethod = Literal["GET", "POST", "HEAD", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]

log: logging.Logger = logging.getLogger("telegrampy.http")

user_agent: str = "TelegramBot (https://github.com/ilovetocode2019/telegram.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"


class Route:
    """Represents a Telegram route"""

    BASE_URL: str = "https://api.telegram.org/bot{0}/"

    if TYPE_CHECKING:
        method: HTTPMethod
        url: str

    def __init__(self, method: HTTPMethod, url: str):
        self.method: HTTPMethod = method
        self.url: str = url

    def __str__(self) -> str:
        return f"{self.method}: {self.url}"


class HTTPClient:
    """Represents an HTTP client making requests to Telegram."""

    def __init__(self, token: str, loop: asyncio.AbstractEventLoop):
        self._token: str = token
        self._base_url: str = Route.BASE_URL.format(self._token)

        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(loop=self.loop, headers={"User-Agent": self.user_agent})

    async def request(self, route: Route, **kwargs: Any) -> Any:
        """Make a request to a route.

        All kwargs will be forwarded to
        :meth:`aiohttp.ClientSession.request`.

        Parameters
        ----------
        route: :class:`telegrampy.http.Route`
            The route to make a request to.
        """
        url = route.url
        method = route.method

        resp: Optional[aiohttp.ClientResponse] = None
        data: Optional[Dict[str, Any]] = None

        # Try a request 5 times before dropping it
        for tries in range(5):
            log.debug(f"Requesting to {method}:{url} (Attempt {tries+1})")

            try:
                async with self.session.request(method, url, timeout=30, **kwargs) as resp:
                    # Telegram docs say all responses will have json
                    data = await resp.json()

                    if not isinstance(data, dict):
                        raise RuntimeError("Response from Telegram is not in JSON format.")

                    if 300 > resp.status >= 200:
                        return data

                    # We are getting ratelimited
                    if resp.status == 429:
                        params = data.get("parameters")

                        if not params:
                            raise HTTPException(resp, data.get("description"))

                        retry_after = params.get("retry_after")

                        # We didn't get a retry after, so raise an HTTPException
                        if not retry_after:
                            raise HTTPException(resp, data.get("description"))

                        log.warning(f"We are being ratelimited. Retrying in {retry_after} seconds.")

                        await asyncio.sleep(retry_after)
                        continue

                    # Unauthorized
                    if resp.status == 400:
                        raise BadRequest(resp, data.get("description"))
                    elif resp.status == 401:
                        raise InvalidToken(resp, data.get("description"))
                    # Forbidden
                    elif resp.status == 403:
                        raise Forbidden(resp, data.get("description"))
                    # Not found
                    if resp.status == 404:
                        raise InvalidToken(resp, data.get("description"))
                    # Conflict with other request
                    elif resp.status == 409:
                        raise Conflict(resp, data.get("description"))
                    # Some sort of internal Telegram error
                    if resp.status >= 500:
                        await asyncio.sleep((1 + tries) * 2)
                        continue
                    else:
                        raise HTTPException(resp, (data).get("description"))
            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep((1 + tries) * 2)
                    continue
                raise

        if resp is not None:
            log.debug(f"Request to to {method}:{url} failed with status code {resp.status}")

            description = data.get("description") if isinstance(data, dict) else data

            if resp.status >= 500:
                raise ServerError(resp, description)
            else:
                raise HTTPException(resp, description)

    async def send_message(self, chat_id: int, content: str, parse_mode: str = None, reply_message_id: int = None) -> Message:
        """Sends a message to a chat."""

        url = self._base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_message_id:
            data["reply_to_message_id"] = reply_message_id

        response = await self.request(Route("POST", url), json=data)

        message = Message(self, response["result"])
        return message

    async def edit_message_content(self, chat_id: int, message_id: int, content: str, parse_mode: str = None) -> Optional[Message]:
        """Edits a message."""

        url = self._base_url + "editMessageText"
        data = {"chat_id": chat_id, "message_id": message_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode

        response = await self.request(Route("POST", url), json=data)

        if response is True:
            return

        edited_message = Message(self, response["result"])
        return edited_message

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        """Deletes a message."""

        url = self._base_url + "deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        await self.request(Route("POST", url), json=data)

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int) -> Message:
        """Forwards a message."""

        url = self._base_url + "forwardMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        response = await self.request(Route("POST", url), json=data)

        forwarded_message = Message(self, response["result"])
        return forwarded_message

    async def send_photo(self, chat_id: int, file: io.BytesIO, filename: str = None, caption: str = None, parse_mode: str = None) -> Message:
        """Sends a photo to a chat."""

        url = self._base_url + "sendPhoto"
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("photo", file, filename=filename)

        if caption:
            writer.add_field("caption", caption)
        if parse_mode:
            writer.add_field("parse_mode", parse_mode)

        response = await self.request(Route("POST", url), data=writer)

        message = Message(self, response["result"])
        return message

    async def send_document(self, chat_id: int, file: io.BytesIO, filename: str = None, caption: str = None, parse_mode: str = None) -> Message:
        """Sends a document to a chat."""

        url = self._base_url + "sendDocument"
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("document", file, filename=filename)

        if caption:
            writer.add_field("caption", caption)
        if parse_mode:
            writer.add_field("parse_mode", parse_mode)

        response = await self.request(Route("POST", url), data=writer)

        message = Message(self, response["result"])
        return message

    async def send_poll(self, chat_id: int, question: str, options: List[str]) -> Poll:
        """Sends a poll to a chat."""

        url = self._base_url + "sendPoll"
        data = {"chat_id": chat_id, "question": question, "options": json.dumps(options)}
        response = await self.request(Route("POST", url), json=data)

        message = Poll(self, response["result"])
        return message

    async def send_chat_action(self, chat_id: int, action: str) -> None:
        """Sends a chat action to a chat."""

        url = self._base_url + "sendChatAction"
        data = {"chat_id": chat_id, "action": action}
        await self.request(Route("POST", url), json=data)

    async def get_chat(self, chat_id: int) -> Chat:
        """Fetches a chat."""

        url = self._base_url + "getChat"
        data = {"chat_id": chat_id}
        response = await self.request(Route("GET", url), json=data)

        return Chat(self, response["result"])

    async def get_chat_member(self, chat_id: int, user_id: int) -> User:
        """Fetches a member from a chat."""

        url = self._base_url + "getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        response = await self.request(Route("GET", url), json=data)

        return User(self, response["result"].get("user"))

    async def get_me(self) -> User:
        """Fetches the bot account."""

        url = self._base_url + "getMe"
        response = await self.request(Route("GET", url))

        return User(self, response["result"])

    async def get_updates(
        self,
        offset: int = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Sequence[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetches the new updates for the bot."""

        url = self._base_url + "getUpdates"
        data = {"offset": offset, "limit": limit, "timeout": timeout, "allowed_updates": allowed_updates}
        response = await self.request(Route("POST", url), json=data)

        return response["result"]

    async def close(self) -> None:
        """Closes the HTTP session."""

        await self.session.close()
