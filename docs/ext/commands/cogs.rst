.. _ext_commands_cogs:

Introduction to Cogs
====================

At some point you may want to separate commands into categories.
That's what cogs are for. They allow you to group commands into categories using classes.

Usually, cogs are used with `extensions <extensions.html>`__.


Example Cog
~~~~~~~~~~~

.. code-block:: python

    import telegrampy
    from telegrampy.ext import commands

    class Cog(commands.Cog):

        def __init__(self, bot):
            self.bot = bot

        @commands.command()
        async def command(self, ctx):
            pass

    bot = commands.Bot("token here")
    bot.add_cog(Cog(bot))
    bot.run()
