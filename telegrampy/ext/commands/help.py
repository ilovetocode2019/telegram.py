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

import html
import itertools
import typing

import telegrampy

from .core import Command
from .cog import Cog


class _HelpCommandImplementation(Command):
    """Class that interfaces with :class:`telegrampy.ext.commands.Command`."""

    def __init__(self, help_cmd, bot, command_attrs):
        self.help_cmd = help_cmd

        super().__init__(help_cmd, **command_attrs)
        self.bot = bot

class HelpCommand:
    """Help command template.

    Attributes
    ----------
    ctx: :class:`telegrampy.ext.commands.Context`
        The :class:`telegrampy.ext.commands.Context` for the command
    bot: :class:`telegrampy.ext.commands.Bot`
        The :class:`telegrampy.ext.commands.Bot` from the Context
    """

    def __init__(self, **options):
        self.command_attrs = options.pop('command_attrs', {})
        self.command_attrs.setdefault("name", "help")
        self.command_attrs.setdefault("description", "The help command")
        self.command_attrs.setdefault("aliases", ["start"])

        self._implementation = None

    def _add_to_bot(self, bot):
        implementation = _HelpCommandImplementation(self, bot, self.command_attrs)
        bot.add_command(implementation)
        self._implementation = implementation

    def _remove_from_bot(self, bot):
        bot.remove_command(self._implementation.name)
        self._implementation = None

    async def get_command_signature(self, command):
        """The method that gets a formatted command signature

        Example:
        /help [command]
        """
        name = html.escape(command.name)
        sig = html.escape(command.signature)
        return f"/{name} {sig}"

    async def send_bot_help(self):
        """The method that sends help for the bot.

        This is called when no query is provided.
        This method should handle the sending of the help message.
        """
        raise NotImplementedError("Subclasses must implement this.")

    async def send_cog_help(self, cog: Cog):
        """The method that sends help for a cog.

        This is called when a cog matches the query.
        This method should handle the sending of the help message.

        Parameters
        ----------
        cog: :class:`telegrampy.ext.commands.Cog`
            The cog that matched the query
        """
        raise NotImplementedError("Subclasses must implement this.")

    async def send_command_help(self, command: Command):
        """The method that sends help for a command.

        This is called when a command matches the query.
        This method should handle the sending of the help message.

        Parameters
        ----------
        command: :class:`telegrampy.ext.commands.Command`
            The command that matched the query
        """
        raise NotImplementedError("Subclasses must implement this.")

    async def send_not_found(self, query: str):
        """The method that sends a 'not found' message or similar.

        This method is called when no match is found for the query.

        Parameters
        ----------
        query: :class:`str`
            The user's query
        """
        await self.ctx.send(f"A command or cog named '{query}' was not found.")

    async def help_callback(self, query: typing.Optional[str]):
        """The callback that searches for a matching commmand or cog.

        This should not be overridden unless it is necessary.

        Parameters
        ----------
        query: Optional[:class:`str`]
            The user's query. Defaults to ``None``.
        """
        bot = self.bot

        # Send the bot help if there is no query
        if query is None:
            await self.send_bot_help()
            return

        # Check if the query matches a cog
        cogs = bot.cogs

        if query in cogs.keys():
            cog = cogs[query]
            await self.send_cog_help(cog)
            return

        # If not, check if the query matches a command
        command = bot.get_command(query)
        if command:
            await self.send_command_help(command)
            return

        # If neither, send the not found message
        await self.send_not_found(query)

    async def __call__(self, ctx, *, command=None):
        self.ctx = ctx
        self.bot = ctx.bot
        await self.help_callback(command)


class DefaultHelpCommand(HelpCommand):
    """The default help command.

    This help command mimics BotFather's help command look.

    Parameters
    ----------
    no_category: Optional[:class:`str`]
        The heading for commands without a category.
        Defaults to "No Category".
    sort_commands: Optional[:class:`bool`]
        Whether to sort the commands.
        Defaults to ``True``.
    """

    def __init__(self, **options):
        self.no_category = options.pop("no_category", "No Category")
        self.sort_commands = options.pop("sort_commands", True)
        super().__init__(**options)

    def get_ending_note(self):
        """Returns the command's ending note."""
        name = self._implementation.name
        return (
            f"Type /{name} [command] for more info on a command.\n"
            f"You can also type /{name} [category] for more info on a category."
        )

    async def format_commands(self, commands: typing.List[Command], *, heading: str):
        """The method that formats a given list of commands.

        Parameters
        ----------
        commands: List[:class`telegrampy.ext.commands.Command`]
            The list of commands to format.
        heading: :class:`str`
            The heading to display.
        """
        if not commands:
            return []

        formatted = []

        formatted.append(f"<b>{html.escape(heading)}:</b>")

        def make_entry(sig, doc, *, alias_for=None):
            alias = f"[Alias for {alias_for}] " if alias_for else ""

            if doc:
                return f"{sig} - {alias}{html.escape(doc)}"
            else:
                entry = f"{sig}"
                if alias:
                    entry += f" {alias}"
                return entry

        for command in commands:
            if command.hidden:
                continue

            sig = await self.get_command_signature(command)
            doc = command.description
            formatted.append(make_entry(sig, doc))

        return formatted

    async def format_command(self, command):
        """The method that formats an indivitual command.

        Parameters
        ------------
        command: :class:`Command`
            The command to format.
        """

        help_text = [await self.get_command_signature(command)]

        if command.description:
            help_text.append(html.escape(command.description))
        if command.aliases:
            help_text.append(f"Aliases: {', '.join(command.aliases)}")

        return help_text

    async def send_help_text(self, help_text):
        message = "\n".join(help_text)
        await self.ctx.send(message, parse_mode="HTML")

    async def send_bot_help(self):
        bot = self.bot

        help_text = []

        if bot.description:
            # <description> portion
            help_text.append(html.escape(bot.description))
            help_text.append("")  # blank line

        no_category = self.no_category

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        to_iterate = itertools.groupby(bot.commands, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = (
                sorted(commands, key=lambda c: c.name)
                if self.sort_commands
                else list(commands)
            )
            added = await self.format_commands(commands, heading=category)
            if added:
                help_text.extend(added)
                help_text.append("")  # blank line

        note = self.get_ending_note()
        if note:
            # help_text.append("")  # blank line
            help_text.append(html.escape(note))

        await self.send_help_text(help_text)

    async def send_cog_help(self, cog: Cog):
        bot = self.bot

        help_text = []

        if cog.description:
            help_text.append(html.escape(cog.description))
            help_text.append("")  # blank line

        help_text.extend(await self.format_commands(cog.commands, heading="Commands"))

        note = self.get_ending_note()
        if note:
            help_text.append("")  # blank line
            help_text.append(html.escape(note))

        await self.send_help_text(help_text)

    async def send_command_help(self, command: Command):
        await self.send_help_text(await self.format_command(command))
