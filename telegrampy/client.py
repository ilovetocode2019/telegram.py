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
import logging
import sys
import traceback
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from .chat import Chat, PartialChat
from .errors import InvalidToken, Conflict
from .http import HTTPClient
from .markup import CallbackQuery, InlineKeyboard
from .member import MemberUpdated
from .message import Message
from .poll import Poll, PollAnswer
from .user import ClientUser

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    P = ParamSpec("P")
    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    CoroFunc = Callable[..., Coro[Any]]

log: logging.Logger = logging.getLogger(__name__)


class Client:
    """A client that polls updates and make requests to Telegram.

    Parameters
    ----------
    token: :class:`str`
        The bot token used to authenticate the account.
    loop: :class:`asyncio.AbstractEventLoop` | None
        The event loop associated with the client.
        Uses :func:`asyncio.get_event_loop` if left unspecified.
    timeout: :class:`int`
        The long polling timeout in seconds. Defaults to ``10``.
    api_url: :class:`str`
        The URL of a selfhosted API server. Otherwise, Telegram's servers will be used.
    api_is_local: :class:`bool`
        Whether the API server is in local mode.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the bot is running on.
    """

    def __init__(
        self,
        token: str,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        timeout: int = 10,
        api_url: str = "https://api.telegram.org",
        is_local: bool = False
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.http: HTTPClient = HTTPClient(token=token, loop=self.loop, api_url=api_url, is_local=is_local)

        self._running: bool = False
        self._last_update_id: int | None = None
        self._timeout: int = timeout

        self._listeners: dict[str, list[CoroFunc]] = {}
        self._waiting_for: dict[str, list[tuple[asyncio.Future, Callable[..., bool]]]] = {}

    async def get_me(self) -> ClientUser:
        """|coro|

        Fetches the authenticated bot account.

        Returns
        -------
        :class:`telegrampy.ClientUser`:
            The user that was fetched.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Fetching the bot user failed.
        """

        result = await self.http.get_me()
        return ClientUser(self.http, result)

    async def get_chat(self, chat_id: int) -> Chat:
        """|coro|

        Fetches a chat by ID.

        Parameters
        ----------
        chat_id: :class:`int`
            The ID of the chat to fetch.

        Returns
        -------
        :class:`telegrampy.Chat`
            The chat that was fetched.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Fetching the chat failed.
        """

        result = await self.http.get_chat(chat_id=chat_id)
        return Chat(self.http, result)

    async def set_name(self, name: str | None, *, language_code: str | None = None) -> None:
        """|coro|

        Sets the description that is shown for the bot.

        Parameters
        ----------
        name: :class:`str`
            The display name of the bot, no longer than 64 chatacters.
        """

        await self.http.set_my_name(name=name, language_code=language_code)

    async def set_description(
        self,
        description: str | None,
        *,
        language_code: str | None = None,
        short: bool = False
    ) -> None:
        """|coro|

        Sets the description that is shown for the bot.

        Parameters
        ----------
        description: :class:`str`
            The new description.
            Maxmium of 512 characters for full description and 120 for short description.
        language_code: :class:`str`
            The two-letter ISO 639-1 language code for this description.
        short: :class:`str`
            Whether to set the short or full description.
            The full description appears on empty chats with the bot, while the long decription appears on the profile page.
        """

        if short:
            await self.http.set_my_short_description(short_description=description, language_code=language_code)
        else:
            await self.http.set_my_description(description=description, language_code=language_code)

    def get_partial_chat(self, chat_id) -> PartialChat:
        """Returns a partial chat for the given ID, without fetching anything from Telegram.

        This is useful for interacting with chat that you have an ID for, without making extra API calls.

        Returns
        -------
        :class:`telegrampy.PartialChat`
            The partial chat that can be interacted with.
        """

        return PartialChat(self.http, chat_id)

    def add_inline_keyboard(self, message_id: int, keyboard: InlineKeyboard) -> None:
        """Binds :class:`.InlineKeyboard` to a specific message on the client, to listen for updates.
        This is intended to be used when you want the inline keyboard to last longer than the lifecycle of the program.
        """

        self.http.inline_keyboard_state.add(message_id, keyboard)

    async def _poll(self) -> None:
        await self.setup_hook()
        tries = 0

        log.info("Polling updates from server...")

        while self._running:
            try:
                updates = await self.http.get_updates(offset=self._last_update_id, timeout=self._timeout)
            except (InvalidToken, Conflict):
                raise
            except Exception as exc:
                if self._running:
                    if tries < 30:
                        tries += 1
                    log.error(f"Failure while polling updates. Retrying in {tries * 2} seconds.", exc_info=exc)
                    await asyncio.sleep(tries * 2)
            else:
                if updates:
                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                    log.debug(f"Handling updates: {update_ids}")
                    for update in updates:
                        await self._handle_update(update)

                tries = 0

    async def _handle_update(self, update: dict[str, Any]) -> None:
        update_id = update["update_id"]

        self.dispatch("raw_update", update)

        if "message" in update:
            message = Message(self.http, update["message"])
            self.dispatch("message", message)
        elif "edited_message" in update:
            message = Message(self.http, update["edited_message"])
            self.dispatch("message_edit", message)
        elif "channel_post" in update:
            message = Message(self.http, update["channel_post"])
            self.dispatch("post", message)
        elif "edited_channel_post" in update:
            message = Message(self.http, update["edited_channel_post"])
            self.dispatch("post_edit", message)
        elif "callback_query" in update:
            query = CallbackQuery(self.http, update["callback_query"])
            self.dispatch("callback_query", query)
            self.http.inline_keyboard_state.dispatch(query)
        elif "poll" in update:
            poll = Poll(self.http, update["poll"])
            self.dispatch("poll", poll)
        elif "poll_answer" in update:
            answer = PollAnswer(self.http, update["poll_answer"])
            self.dispatch("poll_answer", answer)
        elif "my_chat_member" in update:
            member_updated = MemberUpdated(self.http, update["my_chat_member"])
            self.dispatch("member_update", member_updated)
        elif "chat_member" in update:
            member_updated = MemberUpdated(self.http, update["chat_member"])
            self.dispatch("member_update", member_updated)
        else:
            log.warning(f"Received an unknown update: {update}")

    async def _use_event_handler(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except Exception as exc:
            self.dispatch("error", exc)

    def dispatch(self, event: str, *args: Any) -> None:
        log.debug(f"Dispatching {event} with {args}")

        # Handle the active wait_fors
        waiting_for = self._waiting_for.get(event)
        if waiting_for:
            removed_futures = []
            for i, (future, check) in enumerate(waiting_for):
                if future.cancelled():
                    removed_futures.append(i)
                    continue

                # Run the check associated with the future
                # and set the future's result or exception
                try:
                    result = check(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed_futures.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed_futures.append(i)

            # Clean up waiting_for
            if len(removed_futures) == len(waiting_for):
                self._waiting_for.pop(event)
            else:
                for idx in reversed(removed_futures):
                    del waiting_for[idx]

        # Add "on_" to the event name
        event = f"on_{event}"

        # Get the listeners for the event
        if event in self._listeners:
            handlers = self._listeners[event]
        else:
            handlers = []

        try:
            handlers.append(getattr(self, event))
        except AttributeError:
            pass

        # Dispatch the event to the listeners
        for handler in handlers:
            self.loop.create_task(self._use_event_handler(handler, *args))

    # TODO: Add overloads
    async def wait_for(self, event: str, *, check: Callable[..., bool] | None = None, timeout: float | None = None) -> Any:
        """|coro|

        Waits for an event.

        Parameters
        ----------
        event: :class:`str`
            The name of the event to wait for.
        """
        ev = event.lower()

        if check is None:
            def _check(*args):
                return True
            check = _check

        future = self.loop.create_future()

        try:
            waiting_for = self._waiting_for[ev]
        except KeyError:
            waiting_for = []
            self._waiting_for[ev] = waiting_for

        waiting_for.append((future, check))

        return await asyncio.wait_for(future, timeout=timeout)

    def event(self, func: CoroFunc) -> CoroFunc:
        """Turns a function into an event handler.

        Parameters
        ----------
        func:
            The function to make an event handler.
        """

        setattr(self, func.__name__, func)
        return func

    def add_listener(self, func: CoroFunc, name: str | None = None) -> None:
        """Registers a function as a listener.

        Parameters
        ----------
        func:
            The function to register.
        name: :class:`str` | None
            The name of the event to register the function as.
        """

        name = name or func.__name__

        if name in self._listeners:
            self._listeners[name].append(func)
        else:
            self._listeners[name] = [func]

    def remove_listener(self, func: CoroFunc) -> None:
        """Removes a listener.

        Parameters
        ----------
        func:
            The function that is registered as a listener.
        """

        for event in self._listeners:
            if func in self._listeners[event]:
                self._listeners[event].remove(func)

    def listen(self, name: str | None = None) -> Callable[[CoroFunc], CoroFunc]:
        """A decorator that registers a function as a listener.

        Parameters
        ---------
        name: :class:`str` | None
            The name of the event to register the function as.
        """

        def deco(func: CoroFunc) -> CoroFunc:
            self.add_listener(func, name)
            return func

        return deco

    async def on_error(self, error: Exception) -> None:
        if "on_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def start(self) -> None:
        """|coro|

        Starts the bot.

        Raises
        ------
        :exc:`RuntimeError`
            This instance of the bot is already running.
        """

        if self._running:
            raise RuntimeError("Bot is already running")

        log.info("Starting the bot")

        self._running = True
        await self._poll()

    async def stop(self) -> None:
        """|coro|

        Stops the bot.

        Raises
        ------
        :exc:`RuntimeError`
            This instance of the bot is not running.
        """

        if not self._running:
            raise RuntimeError("Bot is not running")

        log.info("Stopping the bot")

        self._running = False
        await self.http.close()

    async def setup_hook(self) -> None:
        """|coro|

        Called before the bot begins polling updates.
        This is meant to be overrided by subclasses that require asynchronous setup.
        """

        pass

    def _clean_tasks(self) -> None:
        tasks = asyncio.all_tasks(loop=self.loop)
        if not tasks:
            return

        for task in tasks:
            task.cancel()

        self.loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())

    def run(self) -> None:
        """Runs the bot."""

        self._running = True

        try:
            self.loop.run_until_complete(self._poll())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.stop())

        self._clean_tasks()
        self.loop.close()
