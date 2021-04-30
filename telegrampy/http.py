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

import asyncio
import datetime
import json
import io
import logging
import sys

import aiohttp

from . import __version__
from .errors import *
from .user import User
from .chat import Chat
from .message import Message
from .poll import *

log = logging.getLogger("telegrampy.http")

user_agent = "TelegramBot (https://github.com/ilovetocode2019/telegram.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"


class Route:
    """Represents a Telegram route"""

    BASE_URL = ""

    def __init__(self, method, url):
        self.method = method
        self.url = url

    def __str__(self):
        return f"{self.method}: {self.url}"


class HTTPClient:
    """Represents an HTTP client making requests to Telegram."""

    def __init__(self, token: str, loop: asyncio.BaseEventLoop):
        self._token = token
        self._base_url = f"https://api.telegram.org/bot{self._token}/"

        self.loop = loop or asyncio.get_event_loop()
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        self.session = aiohttp.ClientSession(loop=self.loop, headers={"User-Agent": self.user_agent})

    async def request(self, route: Route, **kwargs):
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

        # Try a request 5 times before dropping it
        for tries in range(5):
            log.debug(f"Requesting to {method}:{url} (Attempt {tries+1})")

            async with self.session.request(method, url, timeout=30, **kwargs) as resp:
                # Telegram docs say all responses will have json
                data = await resp.json()

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

        log.debug(f"Request to to {method}:{url} failed with status code {resp.status}")

        if resp.status >= 500:
            raise ServerError(resp, data.get("description"))
        else:
            raise HTTPException(resp, data.get("description"))

    async def send_message(self, chat_id: int, content: str, parse_mode: str = None, reply_message_id: int = None):
        """Sends a message to a chat."""

        url = self._base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_message_id:
            data["reply_to_message_id"] = reply_message_id

        response = await self.request(Route("POST", url), json=data)

        if "result" in response:
            message = Message(self, response["result"])
            return message

    async def edit_message_content(self, chat_id: int, message_id: int, content: str, parse_mode: str = None):
        """Edits a message."""

        url = self._base_url + "editMessageText"
        data = {"chat_id": chat_id, "message_id": message_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode

        response = await self.request(Route("POST", url), json=data)

        if response is True:
            return

        if "result" in response:
            edited_message = Message(self, response["result"])
            return edited_message

    async def delete_message(self, chat_id: int, message_id: int):
        """Deletes a message."""

        url = self._base_url + "deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        await self.request(Route("POST", url), json=data)

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int):
        """Forwards a message."""

        url = self._base_url + "forwardMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        response = await self.request(Route("POST", url), json=data)

        if "result" in response:
            forwarded_message = Message(self, response["result"])
            return forwarded_message

    async def send_photo(self, chat_id: int, file: io.BytesIO, filename: str = None, caption: str = None, parse_mode: str = None):
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

        if "result" in response:
            message = Message(self, response["result"])
            return message

    async def send_document(self, chat_id: int, file: io.BytesIO, filename: str = None, caption: str = None, parse_mode: str = None):
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

        if "result" in response:
            message = Message(self, response["result"])
            return message

    async def send_poll(self, chat_id: int, question: str, options: list):
        """Sends a poll to a chat."""

        url = self._base_url + "sendPoll"
        data = {"chat_id": chat_id, "question": question, "options": json.dumps(options)}
        response = await self.request(Route("POST", url), json=data)

        if "result" in response:
            message = Poll(self, response["result"])
            return message

    async def send_chat_action(self, chat_id: int, action: str):
        """Sends a chat action to a chat."""

        url = self._base_url + "sendChatAction"
        data = {"chat_id": chat_id, "action": action}
        await self.request(Route("POST", url), json=data)

    async def get_chat(self, chat_id: int):
        """Fetches a chat."""

        url = self._base_url + "getChat"
        data = {"chat_id": chat_id}
        response = await self.request(Route("GET", url), json=data)

        if "result" in response:
            return Chat(self, response["result"])

    async def get_chat_member(self, chat_id: int, user_id: int):
        """Fetches a member from a chat."""

        url = self._base_url + "getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        response = await self.request(Route("GET", url), json=data)

        if "result" in response:
            return User(self, response["result"].get("user"))

    async def get_me(self):
        """Fetches the bot account."""

        url = self._base_url + "getMe"
        response = await self.request(Route("GET", url))

        if "result" in response:
            return User(self, response["result"])

    async def get_updates(self, offset=None, limit=100, timeout=0, allowed_updates=None):
        """Fetches the new updates for the bot."""

        url = self._base_url + "getUpdates"
        data = {"offset": offset, "limit": limit, "timeout": timeout, "allowed_updates": allowed_updates}
        response = await self.request(Route("POST", url), json=data)

        if "result" in response:
            return response["result"]

    async def close(self):
        """Closes the HTTP session."""

        await self.session.close()
