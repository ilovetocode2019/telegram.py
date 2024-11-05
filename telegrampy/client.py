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
import logging
import sys
import traceback
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Optional, Tuple, TypeVar

from .errors import InvalidToken, Conflict
from .http import HTTPClient
from .member import MemberUpdated
from .message import Message
from .poll import Poll, PollAnswer

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from .chat import Chat
    from .user import User

    P = ParamSpec("P")

    T = TypeVar('T')

    Coro = Coroutine[Any, Any, T]
    CoroFunc = Callable[..., Coro[Any]]

log: logging.Logger = logging.getLogger("telegrampy")


class Client:
    """Represents a client connection to Telegram.

    Parameters
    ----------
    token: :class:`str`
        The Telegram API token for the bot.
    loop: Optional[:class:`asyncio.BaseEventLoop`]
        The event loop to use for the bot. Uses :func:`asyncio.get_event_loop` is none is specified.
    wait: Optional[:class:`int`]
        The timeout in seconds for long polling. Defaults to 5.
    read_unread_updates: Optional[:class:`bool`]
        If the bot should read unread updates on startup. Defaults to False.

    Attributes
    ----------
    token: :class:`str`
        The Telegram API  token for the bot.
    loop: :class:`asyncio.BaseEventLoop`
        The event loop to use for the bot.
    """

    def __init__(self, token: str, *, loop: asyncio.AbstractEventLoop = None, **options: Any):
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.http: HTTPClient = HTTPClient(token=token, loop=self.loop)

        wait: int = options.get("wait", 10)
        if wait < 1 or wait > 10:
            raise ValueError("Wait time must be between 1 and 10")

        self._running: bool = False
        self._last_update_id: Optional[int] = None
        self._wait: int = wait
        self._read_unread_updates: bool = options.get("read_unread_updates", False)

        self._listeners: Dict[str, List[CoroFunc]] = {}
        self._waiting_for: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}

    async def get_me(self) -> User:
        """|coro|

        Fetches the bot account.

        Returns
        -------
        :class:`telegrampy.User`:
            The user that was fetched.

        Raises
        ------
        :exc:`telegrampy.HTTPException`
            Fetching the bot user failed.
        """

        return await self.http.get_me()

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

        return await self.http.get_chat(chat_id=chat_id)

    async def set_name(self, name: str = None, *, language_code: str = None) -> None:
        await self.http.set_my_name(name, language_code)

    async def _poll(self) -> None:
        # Get last update id
        log.info("Fetching unread updates")
        try:
            updates = await self.http.get_updates(offset=self._last_update_id)
        except Exception:
            raise
        else:
            if updates:
                update_ids = [int(update["update_id"]) for update in updates]
                self._last_update_id = max(update_ids) + 1
                if self._read_unread_updates:
                    log.debug(f"Handling updates: {[update['update_id'] for update in updates]} ({len(updates)}")
                    for update in updates:
                        await self._handle_update(update)

        tries = 0

        # Main loop
        while self._running:
            # Fetch updates
            try:
                updates = await self.http.get_updates(offset=self._last_update_id, timeout=self._wait)
            except (InvalidToken, Conflict):
                raise
            except Exception:
                if self._running:
                    if tries < 30:
                        tries += 1
                    log.warning(f"Couldn't connect to Telegram. Retrying in {tries*2} seconds.")
                    await asyncio.sleep(tries*2)
            else:
                if updates:
                    # Handle them
                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                    log.debug(f"Handling updates: {[update['update_id'] for update in updates]}")
                    for update in updates:
                        await self._handle_update(update)

                tries = 0

        log.info("The bot successfully completed")

    async def _handle_update(self, update: Dict[str, Any]) -> None:
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
        elif "poll" in update:
            poll = Poll(self.http, update["poll"])
            self.dispatch("poll", poll)
        elif "poll_answer" in update:
            answer = PollAnswer(self.http, update["poll_answer"])
            self.dispatch("poll_answer", answer)
        elif "my_chat_member" in update:
            member_update = MemberUpdated(self.http, update["my_chat_member"])
            self.dispatch("member_updated", member_update)
        elif "chat_member" in update:
            member_update = MemberUpdated(self.http, update["chat_member"])
            self.dispatch("member_updated", member_update)
        else:
            log.warning(f"Received an unknown update ({update_id}): {update}")

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

    async def wait_for(self, event: str, *, check: Optional[Callable[..., bool]] = None, timeout: Optional[float] = None):
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

    def add_listener(self, func: CoroFunc, name: str = None) -> None:
        """Registers a function as a listener.

        Parameters
        ----------
        func:
            The function to register.
        name: Optional[:class:`str`]
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

    def listen(self, name: str = None) -> Callable[[CoroFunc], CoroFunc]:
        """A decorator that registers a function as a listener.

        Parameters
        ---------
        name: Optional[:class:`str`]
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
        """

        if self._running:
            raise RuntimeError("Bot is already running")

        log.info("Starting the bot")

        self._running = True
        await self._poll()

    async def stop(self) -> None:
        """|coro|

        Stops the bot.
        """

        if not self._running:
            raise RuntimeError("Bot is not running")

        log.info("Stopping the bot")

        self._running = False
        await self.http.close()

    def _clean_tasks(self) -> None:
        log.info("Cleaning up tasks")
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
            log.info("Running the bot")
            self.loop.run_until_complete(self._poll())
        except KeyboardInterrupt:
            log.info("Received signal to stop bot")
            self.loop.run_until_complete(self.stop())

        self._clean_tasks()
        self.loop.close()
