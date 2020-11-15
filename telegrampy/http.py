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

import asyncio
import datetime
import json
import sys
import logging

import aiohttp

from . import __version__
from .errors import *
from .user import User
from .chat import Chat
from .message import Message
from .file import *
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
        self.messages_dict = {}

        self.loop = loop or asyncio.get_event_loop()
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        self.session = aiohttp.ClientSession(loop=self.loop, headers={"User-Agent": self.user_agent})

    @property
    def messages(self):
        """A cache of messages the bot can see."""

        return list(self.messages_dict.values())

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
            async with self.session.request(method, url, **kwargs) as resp:
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

                    # We didn't get a retry after,
                    # so raise an HTTPException
                    if not retry_after:
                        raise HTTPException(resp, data.get("description"))

                    log.warning(f"We are being ratelimited. Retrying in {retry_after} seconds.")

                    await asyncio.sleep(retry_after)
                    continue

                # Token is invalid
                if resp.status == 403:
                    raise Forbidden(resp, data.get("description"))
                if resp.status in (401, 404):
                    raise InvalidToken(resp, data.get("description"))
                if resp.status == 409:
                    raise Conflict(resp, data.get("description"))

                # Some sort of internal Telegram error.
                # Retry with an increasing sleep gap between.
                if resp.status in [500, 502, 503, 504]:
                    await asyncio.sleep(1 + tries * 2)
                    continue

                else:
                    raise HTTPException(resp, (data).get("description"))

    async def send_message(self, chat_id: int, content: str, parse_mode: str = None, reply_message_id: int = None):
        """Sends a message to a chat."""

        url = self._base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_message_id:
            data["reply_to_message_id"] = reply_message_id

        message_data = await self.request(Route("POST", url), data=data)

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def edit_message_content(self, chat_id: int, message_id: int, content: str, parse_mode: str = None):
        """Edits a message."""

        url = self._base_url + "editMessageText"
        data = {"chat_id": chat_id, "message_id": message_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode

        await self.request(Route("POST", url), data=data)

    async def delete_message(self, chat_id: int, message_id: int):
        """Deletes a message."""

        url = self._base_url + "deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}

        await self.request(Route("POST", url), data=data)

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int):
        """Forwards a message."""

        url = self._base_url + "forwardMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}

        message_data = await self.request(Route("POST", url), data=data)

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def send_document(self, chat_id: int, document: Document, filename: str = None):
        """Sends a document to a chat."""

        url = self._base_url + "sendDocument"

        writer = aiohttp.FormData()
        writer.add_field("document", document, filename=filename)
        writer.add_field("chat_id", str(chat_id))
        message_data = await self.request(Route("POST", url), data=writer)

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def send_photo(self, chat_id: int, photo: Photo, filename: str = None, caption: str = None):
        """Sends a photo to a chat."""

        url = self._base_url + "sendPhoto"
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("photo", photo, filename=filename)

        if caption:
            writer.add_field("caption", caption)

        message_data = await self.request(Route("POST", url), data=writer)

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def send_poll(self, chat_id: int, question: str, options: list):
        """Sends a poll to a chat."""

        url = self._base_url + "sendPoll"
        data = {"chat_id": chat_id, "question": question, "options": json.dumps(options)}

        poll_data = await self.request(Route("POST", url), data=data)

        if "result" in poll_data:
            msg = Poll(poll_data["result"])

    async def send_chat_action(self, chat_id: int, action: str):
        """Sends a chat action to a chat."""

        url = self._base_url + "sendChatAction"
        data = {"chat_id": chat_id, "action": action}

        chat_action_data = await self.request(Route("POST", url), data=data)

    async def get_chat(self, chat_id: int):
        """Fetches a chat."""

        url = self._base_url + "getChat"
        data = {"chat_id": chat_id}
        chat_data = await self.request(Route("GET", url), data=data)

        if "result" in chat_data:
            return Chat(self, chat_data["result"])

    async def get_chat_member(self, chat_id: int, user_id: int):
        """Fetches a member from a chat."""

        url = self._base_url + "getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        user_data = await self.request(Route("GET", url), data=data)

        if "result" in user_data:
            return User(self, user_data["result"].get("user"))

    async def get_me(self):
        url = self._base_url + "getMe"

        me_data = await self.request(Route("GET", url))

        if "result" in me_data:
            return User(self, me_data["result"])

    async def get_updates(self, offset=None):
        """
        Fetches the new updates for the bot.
        """

        url = self._base_url + "getUpdates"

        if not offset:
            data = await self.request(Route("GET", url))

        else:
            data = await self.request(Route("POST", url), data={"offset": offset})

        self._last_update_time = datetime.datetime.now()
        return data["result"]

    async def close(self):
        """Closes the connection."""

        await self.session.close()
