.. _ext_commands_help:

Making a Help Command
=====================

If you don't want to use the default help command you can always make your own help command. To do this you'll need to subclass :class:`telegrampy.ext.commands.HelpCommand`.

You also need to implement send_bot_help, send_cog_help, and send_command_help. This is an example custom help command.

.. code-block:: python

    class MyHelpCommand(commands.HelpCommand):
        async def send_bot_help():
            ctx = self.context
            # Send a menu with info on the bot

        async def send_cog_help(cog):
            ctx = self.context
            # Send a menu with info on the cog passed to the method

        async def send_command_help(command):
            ctx = self.context
            # Send a menu with info on the command passed to the method

Once you have a custom help command, you can set it to the bot like this: ``bot.help_command = MyHelpCommand()``
