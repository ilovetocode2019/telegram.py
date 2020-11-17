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
import logging
import datetime
import traceback
import sys

from .http import HTTPClient
from .errors import *
from .message import Message
from .poll import Poll

log = logging.getLogger("telegrampy")


class Client:
    """
    Represents a client connection to Telegram.

    Parameters
    ----------
    token: :class:`str`
        The API token.
    """

    def __init__(self, token: str):
        self._running = False
        self._last_looped = datetime.datetime.now()

        self.loop = asyncio.get_event_loop()
        self.http = HTTPClient(token=token, loop=self.loop)

        self._listeners = {}
        self._waiting_for = {}

    async def user(self):
        """|coro|

        The user of the bot.
        """

        return await self.http.get_me()

    async def get_chat(self, chat_id: int):
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

    async def _poll(self):
        # Create some variables
        self._last_update_id = None
        self._last_update_time = datetime.datetime.now()
        self._wait_time = 1

        # Get last update id

        while True:
            try:
                log.info("Fetching unread updates")
                updates = await self.http.get_updates(self._last_update_id)
                if len(updates) != 0:
                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                break

            except InvalidToken as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await self.stop()
                return
            except HTTPException as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await asyncio.sleep(10)
            except Exception as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await asyncio.sleep(10)

        # After fetching unread updates, start the loop
        while self._running:
            self._last_looped = datetime.datetime.now()

            try:
                log.debug("Fetching updates")
                updates = await self.http.get_updates(self._last_update_id)
                if len(updates) != 0:
                    log.debug(f"Handling update(s): {[update['update_id'] for update in updates]} ({len(updates)} update(s))")
                    for update in updates:
                        if "message" in update:
                            key = "message"
                            event = "message"
                        elif "edited_message" in update:
                            key = "edited_message"
                            event = "message_edit"
                        elif "poll" in update:
                            key = "poll"
                            event = "poll"

                    data = update[key]

                    if event == "poll":
                        await self._dispatch(event, Poll(data))
                    elif event == "message_edit":
                        await self._dispatch(event, self.http.messages_dict.get(data["message_id"]), Message(self.http, data))
                    else:
                        await self._dispatch(event, Message(self.http, data))

                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                    key = None
                    event = None

                for x in [x for x in updates if "message" in x]:
                    self.http.messages_dict[x["message"]["message_id"]] = Message(self.http, x["message"])
                for x in [x for x in updates if "edited_message" in x]:
                    self.http.messages_dict[x["edited_message"]["message_id"]] = Message(self.http, x["edited_message"])

            except InvalidToken as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await self.stop()
                return
            except HTTPException as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await asyncio.sleep(10)
            except Exception as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                await asyncio.sleep(10)

            log.debug(f"Waiting for {self._wait_time} seconds")
            await asyncio.sleep(self._wait_time)

    async def _use_event_handler(self, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception as exc:
            await self._dispatch("error", exc)

    async def _dispatch(self, event, *args):
        log.debug(f"Dispatchng {event} with {args}")
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

    async def wait_for(self, event: str, check=None, timeout=None):
        """|coro|

        Waits for an event.

        Parameters
        ----------
        event: :class:`str`
            The name of the event to wait for.
        """
        ev = event.lower()

        if not check:
            def check(*args):
                return True

        future = self.loop.create_future()

        try:
            waiting_for = self._waiting_for[ev]
        except KeyError:
            waiting_for = []
            self._waiting_for[ev] = waiting_for

        waiting_for.append((future, check))

        return await asyncio.wait_for(future, timeout=timeout)

    def event(self, func):
        """
        Turns a function into an event handler.

        Parameters
        ----------
        func:
            The function to make an event handler.
        """

        setattr(self, func.__name__, func)
        return func

    async def on_error(self, error):
        """|coro|

        Default error handler.
        """

        if "on_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def add_listener(self, func, name: str = None):
        """
        Registers a function as a listener.

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

    def remove_listener(self, func):
        """
        Removes a listener.

        Parameters
        ----------
        func:
            The function that is registered as a listener.
        """

        for event in self._listeners:
            if func in self._listeners[event]:
                self._listeners[event].remove(func)

    def listen(self, name=None):
        """
        A decorator that registers a function as a listener.

        Parameters
        ---------
        name: Optional[:class:`str`]
             The name of the event to register the function as.
        """

        def deco(func):
            self.add_listener(func, name)
            return func

        return deco

    async def start(self):
        """|coro|
        Starts the bot.
        """

        if self._running:
            raise RuntimeError("Bot is already running")

        self._running = True
        self.loop.create_task(await self._poll())

    async def stop(self):
        """|coro|
        Stops the bot.
        """

        if not self._running:
            raise RuntimeError("Bot is not running")

        log.info("Stopping the bot")
        await self.http.close()
        self._running = False

    def _clean_tasks(self):
        pending = asyncio.all_tasks(loop=self.loop)
        if not pending:
            return

        for task in pending:
            task.cancel()
        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    def run(self):
        """
        Runs the bot.
        """

        self._running = True

        try:
            log.info("Running the bot")
            self.loop.run_until_complete(self._poll())
        except KeyboardInterrupt:
            log.info("Received KeyboardInterrupt, Stopping bot")
            self.loop.run_until_complete(self.stop())
        finally:
            self._clean_tasks()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
