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

import aiohttp

from .errors import HTTPException
from .user import User
from .chat import Chat
from .message import Message
from .file import *
from .poll import *


class HTTPClient:
    """An HTTP client making requests to Telegram"""

    def __init__(self, token: str, loop: asyncio.BaseEventLoop):
        self._token = token
        self._base_url = f"https://api.telegram.org/bot{self._token}/"
        self.messages_dict = {}

        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)

    @property
    def messages(self):
        """A cache of messages the bot can see"""

        return list(self.messages_dict.values())

    async def send_message(self, chat_id: int, content: str, parse_mode: str=None, reply_message_id: int=None):
        """Sends a message to a chat"""

        url = self._base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_message_id:
            data["reply_to_message_id"] = reply_message_id

        resp = await self.session.post(url, data=data)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to send message")

        message_data = await resp.json()

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int):
        """Forwards a message"""

        url = self._base_url + "forwardMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        
        resp = await self.session.post(url, data=data)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to forward message")

    async def send_document(self, chat_id: int, document: Document, filename: str=None):
        """Sends a document to a chat"""

        url = self._base_url + "sendDocument"

        writer = aiohttp.FormData()
        writer.add_field("document", document, filename=filename)
        writer.add_field("chat_id", str(chat_id))
        resp = await self.session.post(url, data=writer)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to send document")

        message_data = await resp.json()

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def send_photo(self, chat_id: int, photo: Photo, filename: str=None, caption: str=None):
        """Sends a photo to a chat"""

        url = self._base_url + "sendPhoto"
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("photo", photo, filename=filename)

        if caption:
            writer.add_field("caption", caption)

        resp = await self.session.post(url, data=writer)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to send photo")

        message_data = await resp.json()

        if "result" in message_data:
            msg = Message(self, message_data["result"])
            self.messages_dict[msg.id] = msg
            return msg

    async def send_poll(self, chat_id: int, question: str, options: list):
        """Sends a poll to a chat"""

        url = self._base_url + "sendPoll"
        data = {"chat_id": chat_id, "question": question, "options": json.dumps(options)}

        resp = await self.session.post(url, data=data)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to send poll")

        poll_data = await resp.json()

        if "result" in poll_data:
            msg = Poll(poll_data["result"])

    async def send_chat_action(self, chat_id: int, action: str):
        """Sends a chat action to a chat"""

        url = self._base_url + "sendChatAction"
        data = {"chat_id": chat_id, "action": action}

        resp = await self.session.post(url, data=data)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to send action")

        chat_action_data = await resp.json()

    async def get_chat(self, chat_id: int):
        """Fetches a chat"""

        url = self._base_url + "getChat"

        resp = await self.session.post(url, data={"chat_id": chat_id})

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to fetch chat")

        chat_data = await resp.json()
        if "result" in chat_data:
            return Chat(self, chat_data["result"])

    async def get_chat_member(self, chat_id: int, user_id: int):
        """Fetches a member from a chat"""

        url = self._base_url + "getChatMember"

        resp = await self.session.post(url, data={"chat_id": chat_id, "user_id": user_id})

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("description") or "Failed to fetch member")

        user_data = await resp.json()
        if "result" in user_data:
            return User(self, user_data["result"].get("user"))

    async def get_me(self):
        url = self._base_url + "getMe"

        resp = await self.session.get(url)

        if resp.status != 200:
            raise HTTPException(resp, (await resp.json()).get("descrption") or "Failed to get info")

        me_data = await resp.json()
        if "result" in me_data:
            return User(self, me_data["result"])

    async def get_updates(self, offset=None):
        """
        Fetches the new updates for the bot
        """

        url = self._base_url + "getUpdates"
        session = self.session

        if not offset:
            resp = await session.get(url=url)

        else:
            resp = await session.post(url=url, data={"offset":offset})

        if resp.status != 200:
            raise HTTPException(resp, message=(await resp.json()).get("result"))

        self._last_update_time = datetime.datetime.now()
        return (await resp.json())["result"]

    async def close(self):
        """Closes the connection"""

        await self.session.close()
