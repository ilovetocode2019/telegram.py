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


class Bot:
    """
    Represents a Telegram bot

    Attributes
    ----------
    owner_id: Optional[:class:`int`]
        The owner's ID
    owner_ids: Optional[List[:class:`int`]]
        The owner IDs
    cogs: Mapping[:class:`str`: :class:`pygram.Cog`]
        A dictonary of cogs that are loaded
    extensions: Mapping[:class:`str`: :class:`types.ModuleType`]
        A dictonary of extensions that are loaded

    Parameters
    ----------
    token: :class:`str`
        The API token
    owner_id: Optional[:class:`int`]
        The owner's ID
    owner_ids: Optional[]
        The owner IDs
    """

    def __init__(self, token: str,  owner_id: int = None, owner_ids: list = None):
        self.owner_id = owner_id
        self.owner_ids = owner_ids

        self._running = False
        self._last_looped = datetime.datetime.now()

        self.loop = asyncio.get_event_loop()
        self.http = HTTPClient(token=token, loop=self.loop)

        self._listeners = {}
        self.commands_dict = {}

        self.cogs = {}
        self.extension_cogs = {}
        self.extensions = {}

    @property
    def commands(self):
        """
        :class:`list`:
            A list of the commands
        """

        return list(self.commands_dict.values())

    def _get_all_command_names(self):
        all_names = []
        for command in self.commands_dict.values():
            all_names.append(command.name)
            all_names.extend(command.aliases)

        return all_names

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

    def get_command(self, name: str):
        """
        Gets a command by name

        Parameters
        ----------
        name: :class:`str`
            The command name

        Returns
        --------
        :class:`pygram.Command`
            The command with the name
        """

        for command in self.commands_dict.values():
            if name in command.aliases or command.name == name:
                return command

    def get_context(self, message: Message):
        """
        Gets context for a given message

        Parameters
        ----------
        message: :class:`pygram.Message`
            The message to get context from

        Returns
        -------
        :class:`pygram.Context`
            The context created
        """

        # Split the message
        splited = message.content.split(" ")

        if len(splited) != 0:
            command_text = splited[0]

            command_text = command_text[1:]
            command = command_text

            # If the command has a bot mention after the command, remove the mention from command_text
            if "@" in command_text:
                finished_command_text = ""
                past_mention = False
                for x in command_text[::-1]:
                    if past_mention:
                        finished_command_text += x
                    elif x == "@":
                        past_mention = True
                command = finished_command_text[::-1]

            command = self.get_command(command)
        else:
            command = None

        kwargs = {"command": command}
        kwargs["args"] = []
        kwargs["kwargs"] = {}
        kwargs["message"] = message
        kwargs["chat"] = message.chat
        kwargs["author"] = message.author
        kwargs["bot"] = self
        return Context(**kwargs)

    def load_extension(self, location: str):
        """
        Loads an extension

        Parameters
        ----------
        location: :class:`str`
            The location of the extension

        Raises
        ------
        :exc:`pygram.ExtensionAlreadyLoaded`
            The extension is already loaded
        :exc:`AttributeError`
            The extension has no setup function
        """

        if location in self.extensions:
            raise ExtensionAlreadyLoaded(location)

        cog = importlib.import_module(location)
        self.extensions[cog.__name__] = cog

        if not hasattr(cog, "setup"):
            raise AttributeError("Extension has no setup function")

        cog.setup(self)

    def unload_extension(self, location: str):
        """
        Unloads an extension

        Parameters
        ----------
        location: :class:`str`
             The location of the extension
        """

        cog_name = self.extension_cogs.get(location)
        if not cog_name:
            raise ExtensionNotLoaded(location)

        self.remove_cog(cog_name)

        self.extension_cogs.pop(location)
        self.extensions.pop(location)

    def reload_extension(self, location: str):
        """
        Reloads an extension

        Parameters
        ----------
        location: :class:`str`
            The location of the extension
        """

        if location not in self.extension_cogs:
            raise ExtensionNotLoaded(location)

        lib = sys.modules[location]
        importlib.reload(lib)
        self.remove_cog(self.extension_cogs[location])

        sys.modules[location].setup(self)

    def add_cog(self, cog: Cog):
        """
        Adds a cog to the bot

        Parameters
        ----------
        cog: :class:`pygram.Cog`
            The cog to add

        Raises
        ------
        :exc:`TypeError`
            The cog is not a subclass of :class:`pygram.Cog` or the cog check is not a method
        """

        if not issubclass(cog.__class__, Cog):
            raise TypeError("Cogs must be a subclass of Cog")

        cog_commands = []
        cog_listeners = []
        for command in dir(cog):
            command = getattr(cog, command)
            # Add the command if object is a command
            if isinstance(command, Command):
                cog_commands.append(command)
                command.bot = self
                command.cog = cog
                self.add_command(command)

            # If object is a method and it has _cog_listener attribute, add the listener
            elif isinstance(command, types.MethodType):
                try:
                    listener_name = command._cog_listener
                    self.add_listener(command, listener_name)
                    cog_listeners.append(command)
                except AttributeError:
                    pass

        # Add cog check if cog check, otherwise make one that automaticly returns True
        if hasattr(cog, "cog_check"):
            if not inspect.ismethod(cog.cog_check):
                raise TypeError("Cog check is not a function")

            cog_check = cog.cog_check
        else:
            def cog_check(context):
                return True
            cog.cog_check = cog_check

        # Set some cog attributes
        cog.name = cog.__class__.__name__
        cog.commands = cog_commands
        cog.listeners = cog_listeners
        self.cogs[cog.name] = cog

        # If cog is from an extension, add the extension to a dict with the cog name as the value
        if str(cog.__module__) != "__main__":
            self.extension_cogs[cog.__module__] = cog.name

    def remove_cog(self, cog: str):
        """
        Removes and cog from the bot

        Parameters
        ----------
        cog: :class:`str`
            The name of the cog to remove
        """

        if cog not in self.cogs:
            return

        for command in self.cogs[cog].commands:
            self.commands_dict.pop(command.name)

        for listener in self.cogs[cog].listeners:
            self.remove_listener(listener)

        self.cogs.pop(cog)

    async def _poll(self):
        logger.info("Bot is started")

        # Create some variables
        self._last_update_id = None
        self._last_update_time = datetime.datetime.now()
        self._wait_time = 1

        # Get last update id

        while True:
            try:
                updates = await self.http.get_updates(self._last_update_id)
                if len(updates) != 0:
                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                break

            except Exception as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                if exc.response.status in (401, 403, 404):
                    await self.stop()
                    return
                await asyncio.sleep(10)

        # After fetching unread updates, start the loop
        while self._running:
            self._last_looped = datetime.datetime.now()

            try:
                updates = await self.http.get_updates(self._last_update_id)
                for x in [x for x in updates if "message" in x]:
                    self.http.messages_dict[x["message"]["message_id"]] = Message(self.http, x["message"])
                for x in [x for x in updates if "edited_message" in x]:
                    self.http.messages_dict[x["edited_message"]["message_id"]] = Message(self.http, x["edited_message"])

                if len(updates) != 0:
                    for update in updates:
                        if "message" in update:
                            key = "message"
                            event = "message"
                        elif "edited_message" in update:
                            key = "edited_message"
                            event = "edit"
                        elif "poll" in update:
                            key = "poll"
                            event = "poll"

                    data = update[key]

                    if event == "poll":
                        await self._dispatch(event, Poll(data))
                    else:
                        await self._dispatch(event, Message(self.http, data))

                    update_ids = [int(update["update_id"]) for update in updates]
                    self._last_update_id = max(update_ids) + 1
                    key = None
                    event = None

            except Exception as exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
                if exc.response.status in (401, 403, 404):
                    await self.stop()
                    return
                await asyncio.sleep(10)

            await asyncio.sleep(self._wait_time)

        logger.info("Bot is finished")

    async def _use_event_handler(self, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception as exc:
            await self._dispatch("error", exc)

    async def _use_command(self, ctx):
        try:
            await ctx.command.invoke(ctx)
        except Exception as exc:
            await self._dispatch("command_error", ctx, exc)

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

    async def on_command_error(self, ctx, error):
        """Default command error handler"""

        if "on_command_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def on_error(self, error):
        """Default error handler"""

        if "on_error" in self._listeners:
            return

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def command(self, *args, **kwargs):
        """
        Turns a function into a command

        Parameters
        ----------
        \*args:
            The arguments
        \*\*kwargs:
            The keyword arguments
        """

        def deco(func):
            name = kwargs.get("name") or func.__name__

            kwargs["name"] = name
            if name in self._get_all_command_names():
                raise CommandRegistrationError(name)

            command = Command(func, **kwargs)
            command.checks = getattr(func, "_command_checks", [])

            self.commands_dict[name] = command
            return command

        return deco

    def add_command(self, command):
        """
        Adds a command

        Parameters
        ----------
        command: :class:`pygram.Command`
            The command to add

        Returns
        -------
        :class:`pygram.Command`
            The command added

        Raises
        ------
        :exc:`pygram.CommandRegistrationError`
            The command name or one if its aliases is already registered by a different command
        :exc:`TypeError`
            The command is not an instance of :class:`pygram.Command`
        """

        if not isinstance(command, Command):
            raise TypeError("Command must be a subclass of Command")

        if command.name in self._get_all_command_names():
            raise CommandRegistrationError(command.name)

        self.commands_dict[command.name] = command
        return command

    def remove_command(self, name: str):
        """
        Removes a command by name

        Parameters
        ----------
        name: :class:`str`
            The name of the command to remove

        Returns
        -------
        :class:`pygram.Command`:
            The command removed
        """

        command = self.get_command(name)

        if not command:
            return

        self.commands_dict.pop(name)

        return command

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
