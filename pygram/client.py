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
import inspect
import types
import importlib

from .http import HTTPClient
from .errors import *
from .message import Message
from .context import Context
from .poll import Poll
from .core import Command
from .cog import Cog

logger = logging.getLogger("pygram")


class Client:
    """
    Represents a client connection to Telegram

    Parameters
    ----------
    token: :class:`str`
        The API token
    """

    def __init__(self, token: str):
        self._running = False
        self._last_looped = datetime.datetime.now()

        self.loop = asyncio.get_event_loop()
        self.http = HTTPClient(token=token, loop=self.loop)

        self._listeners = {}

    async def user(self):
        """The user of the bot"""

        return await self.http.get_me()

    async def get_chat(self, chat_id: int):
        """
        Fetches a chat by ID

        Parameters
        ----------
        chat_id: :class:`int`
            The ID of the chat to fetch

        Returns
        -------
        :class:`pygram.Chat`
            The chat that was fetched

        Raises
        ------
        :exc:`pygram.HTTPException`
            Fetching the chat failed
        """

        return await self.http.get_chat(chat_id=chat_id)

    async def _use_event_handler(self, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception as exc:
            await self._dispatch("error", exc)

    async def _dispatch(self, event, *args):
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

        # If event is on_message, check if the message if a command
        # If it is a command, invoke the command
        if event == "on_message":
            message = args[0]
            if not message.content:
                return

            ctx = self.get_context(message)

            if not ctx.command:
                return

            self.loop.create_task(self._use_command(ctx))

    async def wait_for(self, event: str, check=None, timeout=None):
        """
        Waits for an event

        Parameters
        ----------
        event: :class:`str`
            The name of the event to wait for
        """

        name = f"on_{event}"
        event = asyncio.Event()

        if not check:
            def check(*args):
                return True

        async def wait_listener(*args):
            if check(*args):
                event.set()

        self.add_listener(wait_listener, name)
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            self.remove_listener(wait_listener)
        except:
            self.remove_listener(wait_listener)
            raise

    def event(self, func):
        """
        Turns a function into an event handler

        Parameters
        ----------
        func:
            The function to make an event handler
        """

        setattr(self, func.__name__, func)
        return func

    async def on_error(self, error):
        """Default error handler"""

        if "on_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def add_listener(self, func, name: str = None):
        """
        Registers a function as a listener

        Parameters
        ----------
        func:
            The function to register
        name: Optional[:class:`str`]
            The name of the event to register the function as
        """

        name = name or func.__name__

        if name in self._listeners:
            self._listeners[name].append(func)
        else:
            self._listeners[name] = [func]

    def remove_listener(self, func):
        """
        Removes a listener

        Parameters
        ----------
        func:
            The function that is registered as a listener
        """

        for event in self._listeners:
            if func in self._listeners[event]:
                self._listeners[event].remove(func)

    def listen(self, name=None):
        """
        A decorator that registers a function as a listener

        Parameters
        ---------
        name: Optional[:class:`str`]
             The name of the event to register the function as
        """

        def deco(func):
            self.add_listener(func, name)
            return func

        return deco

    async def stop(self):
        """Stops the bot"""

        if not self._running:
            raise RuntimeError("Bot is not running")

        await self.http.close()
        self._running = False

    def _clean_tasks(self):
        pending = asyncio.all_tasks(loop=self.loop)
        if not pending:
            return

        logger.info(f"Cleaning up {len(pending)} task(s)")
        for task in pending:
            task.cancel()
        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    def run(self):
        """Runs the bot"""

        self._running = True

        try:
            self.loop.run_until_complete(self._poll())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt, Finishing bot")
            self.loop.run_until_complete(self.stop())
        finally:
            self._clean_tasks()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
