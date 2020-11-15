.. _ext_commands_extensions:

Introduction to Extensions
==========================

Using Extensions
~~~~~~~~~~~~~~~~

Extensions are good for organizing your bot into files and quickly reloading stuff while your bot is running.

An extension at is basicly just a file with a setup function. The setup function cannot be a coroutine and must have a bot parameter.

This is a basic extension.

.. code-block:: python
    :caption: extension.py

    from telegrampy.ext import commands

    @commands.command()
    async def hello(ctx):
        await ctx.send("Hello!")

    def setup(bot):
        bot.add_command(hello)

To load an extension you can use ``bot.load_extension("extension.py")``

To reload an extension you can use ``bot.reload_extension("extension.py")``

To remove an extension you can use ``bot.unload_extension("extension.py")``

Extensions are normally used for cog like this.

.. code-block:: python

    from telegrampy.ext import commands

    class Hello(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.command()
        async def hello(self, ctx):
            await ctx.send("Hello!")

    def setup(bot):
        bot.add_command(Hello(bot))
