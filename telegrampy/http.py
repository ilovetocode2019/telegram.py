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

import asyncio
import io
import json
import logging
import sys
from typing import TYPE_CHECKING, Any

import aiohttp

from . import __version__
from .errors import ClientException, HTTPException, BadRequest, InvalidToken, Forbidden, Conflict, ServerError
from .markup import InlineKeyboardState

if TYPE_CHECKING:
    from .types.chat import Chat as ChatPayload
    from .types.file import File as FilePayload
    from .types.member import Member as MemberPayload
    from .types.message import Message as MessagePayload
    from .types.poll import Poll as PollPayload
    from .types.user import User as UserPayload, UserProfilePhotos as UserProfilePhotosPayload

log: logging.Logger = logging.getLogger(__name__)


class HTTPClient:
    """Represents an HTTP client making requests to Telegram."""

    def __init__(
        self,
        *,
        token: str,
        loop: asyncio.AbstractEventLoop,
        api_url: str,
        is_local: bool,
    ) -> None:
        self._token: str = token
        self._api_url: str = api_url
        self.is_local: bool = is_local
        self.loop: asyncio.AbstractEventLoop = loop
        self.user_agent: str = f"TelegramBot (https://github.com/ilovetocode2019/telegram.py {__version__}) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}"
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(loop=self.loop, headers={"User-Agent": self.user_agent})
        self.inline_keyboard_state: InlineKeyboardState = InlineKeyboardState(self)

    async def request(self, route: str, **kwargs: Any) -> Any:
        for tries in range(5):
            log.debug(f"Requesting to /{route} with payload {kwargs.get('json', {})} (Attempt {tries+1})")

            async with self.session.post(f"{self._api_url}/bot{self._token}/{route}", **kwargs) as resp:
                data = await resp.json()

                if data["ok"] is True:
                    return data["result"]

                description = data["description"]
                parameters = data.get("parameters")

                if parameters is not None and "retry_after" in parameters and tries < 4:
                    log.warning(f"We are being ratelimited at /{route}. Retrying in {parameters['retry_after']} seconds.")
                    await asyncio.sleep(parameters["retry_after"])
                    continue

                if resp.status == 400:
                    raise BadRequest(resp, description)
                elif resp.status in (401, 404):
                    raise InvalidToken(resp, description)
                elif resp.status == 403:
                    raise Forbidden(resp, description)
                elif resp.status == 409:
                    raise Conflict(resp, description)
                elif resp.status >= 500:
                    raise ServerError(resp, description)
                else:
                    raise HTTPException(resp, description)

    async def fetch_file(self, file_path: str) -> bytes:
        if self.is_local is True:
            raise ClientException("Unable to download files from server in local mode.")

        async with self.session.get(f"https://api.telegram.org/file/bot{self._token}/{file_path}") as resp:
            if resp.status != 200:
                data = await resp.json()
                raise HTTPException(resp, data["description"])
            return await resp.read()

    async def send_message(
        self,
        *,
        chat_id: int,
        content: str,
        parse_mode: str | None,
        reply_markup:dict[str, Any] | None,
        reply_message_id: int | None = None,
    ) -> MessagePayload:
        data = {"chat_id": chat_id, "text": content}

        if parse_mode is not None:
            data["parse_mode"] = parse_mode
        if reply_markup is not None:
            data["reply_markup"] = reply_markup
        if reply_message_id is not None:
            data["reply_to_message_id"] = reply_message_id

        return await self.request("sendMessage", json=data)

    async def edit_message_content(
        self,
        *,
        chat_id: int,
        message_id: int,
        content: str,
        parse_mode: str | None
    ) -> MessagePayload | None:
        data = {"chat_id": chat_id, "message_id": message_id, "text": content}

        if parse_mode:
            data["parse_mode"] = parse_mode

        return await self.request("editMessageText", json=data)

    async def delete_message(self, *, chat_id: int, message_id: int) -> None:
        data = {"chat_id": chat_id, "message_id": message_id}
        await self.request("deleteMessage", json=data)

    async def forward_message(self, *, chat_id: int, from_chat_id: int, message_id: int) -> MessagePayload:
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        return await self.request("forwardMessage", json=data)

    async def send_photo(
        self,
        *,
        chat_id: int,
        file: io.BytesIO,
        filename: str | None,
        caption: str | None,
        parse_mode: str | None,
        reply_markup: dict[str, Any] | None
    ) -> MessagePayload:
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("photo", file, filename=filename)

        if caption is not None:
            writer.add_field("caption", caption)
        if parse_mode is not None:
            writer.add_field("parse_mode", parse_mode)
        if reply_markup is not None:
            writer.add_field("reply_markup", reply_markup)

        return await self.request("sendPhoto", data=writer)

    async def send_document(
        self,
        *,
        chat_id: int,
        file: io.BytesIO,
        filename: str | None,
        caption: str | None,
        parse_mode: str | None,
        reply_markup: dict[str, Any] | None
    ) -> MessagePayload:
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("document", file, filename=filename)

        if caption is not None:
            writer.add_field("caption", caption)
        if parse_mode is not None:
            writer.add_field("parse_mode", parse_mode)
        if reply_markup is not None:
            writer.add_field("reply_markup", reply_markup)

        return await self.request("sendDocument", data=writer)

    async def send_poll(
        self,
        *,
        chat_id: int,
        question: str,
        options: list[str]
    ) -> PollPayload:
        data = {"chat_id": chat_id, "question": question, "options": json.dumps(options)}
        return await self.request("sendPoll", json=data)

    async def send_chat_action(self, *, chat_id: int, action: str) -> None:
        data = {"chat_id": chat_id, "action": action}
        await self.request("sendChatAction", json=data)

    async def get_file(self, *, file_id: str) -> FilePayload:
        data = {"file_id": file_id}
        return await self.request("getFile", json=data)

    async def get_chat(self, *, chat_id: int) -> ChatPayload:
        data = {"chat_id": chat_id}
        return await self.request("getChat", json=data)

    async def get_chat_member(self, *, chat_id: int, user_id: int) -> MemberPayload:
        data = {"chat_id": chat_id, "user_id": user_id}
        return await self.request("getChatMember", json=data)

    async def get_user_profile_photos(self, *, user_id: int, offset: int | None, limit: int | None) -> UserProfilePhotosPayload:
        data = {"user_id": user_id}

        if offset is not None:
            data["offset"] = offset
        if limit is not None:
            data["limit"] = limit

        return await self.request("getUserProfilePhotos", json=data)

    async def set_chat_photo(self, *, chat_id: int, photo: io.BytesIO) -> None:
        writer = aiohttp.FormData()
        writer.add_field("chat_id", str(chat_id))
        writer.add_field("photo", photo)
        await self.request("setChatPhoto", data=writer)

    async def delete_chat_photo(self, *, chat_id: int) -> None:
        data = {"chat_id": chat_id}
        await self.request("deleteChatPhoto", json=data)

    async def set_chat_title(self, *, chat_id: int, title: str) -> None:
        data = {"chat_id": chat_id, "title": title}
        await self.request("setChatTitle", json=data)

    async def set_chat_description(self, *, chat_id: int, description: str | None) -> None:
        data: dict[str, Any] = {"chat_id": chat_id}

        if description:
            data["description"] = description

        await self.request("setChatDescription", json=data)

    async def pin_chat_message(
        self,
        *,
        chat_id: int,
        message_id: int,
        disable_notification: bool = False
    ) -> None:
        data = {"chat_id": chat_id, "message_id": message_id, "disable_notification": disable_notification}
        await self.request("pinChatMessage", json=data)

    async def unpin_chat_message(self, *, chat_id: int, message_id: int) -> None:
        data = {"chat_id": chat_id, "message_id": message_id}
        await self.request("unpinChatMessage", json=data)

    async def unpin_all_chat_messages(self, *, chat_id: int) -> None:
        data = {"chat_id": chat_id}
        await self.request("unpinAllChatMessages", json=data)

    async def leave_chat(self, *, chat_id: int) -> None:
        data = {"chat_id": chat_id}
        await self.request("leaveChat", json=data)

    async def get_chat_member_count(self, *, chat_id: int) -> int:
        data = {"chat_id": chat_id}
        return await self.request("getChatMemberCount", json=data)

    async def get_me(self) -> UserPayload:
        return await self.request("getMe")

    async def get_updates(
        self,
        *,
        offset: int | None = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: list[str] | None = None
    ) -> list[dict[str, Any]]:
        data = {"offset": offset, "limit": limit, "timeout": timeout, "allowed_updates": allowed_updates}
        return await self.request("getUpdates", json=data)

    async def set_my_name(self, *, name: str | None, language_code: str | None) -> None:
        data = {"name": name or ""}

        if language_code:
            data["language_code"] = language_code

        await self.request("setMyName", json=data)

    async def set_my_description(self, *, description: str | None, language_code: str | None) -> None:
        data = {"description": description or ""}

        if language_code:
            data["language_code"] = language_code

        await self.request("setMyDescription", json=data)

    async def set_my_short_description(self, *, short_description: str | None, language_code: str | None) -> None:
        data = {"short_description": short_description or ""}

        if language_code:
            data["language_code"] = language_code

        await self.request("setMyShortDescription", json=data)

    async def set_my_commands(self, *, commands: list[dict[str, Any]], language_code: str | None = None) -> None:
        data: dict[str, Any] = {"commands": commands}

        if language_code:
            data["language_code"] = language_code

        await self.request("setMyCommands", json=data)

    async def answer_callback_query(
        self,
        *,
        callback_query_id: str,
        text: str | None,
        show_alert: bool,
        url: str | None,
        cache_time: int | None
    ) -> None:
        data: dict[str, Any] = {"callback_query_id": callback_query_id}

        if text is not None:
            data["text"] = text
        if show_alert is not None:
            data["show_alert"] = show_alert
        if url is not None:
            data["url"] = url
        if cache_time is not None:
            data["cache_time"] = cache_time

        await self.request("answerCallbackQuery", json=data)

    async def close(self) -> None:
        await self.session.close()
