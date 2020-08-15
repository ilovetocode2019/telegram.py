.. _quickstart:

Quickstart
==========

.. _basic example:

Basic Example
-------------

To get started with telegram.py, we'll go over a quick example
line-by-line.

.. code-block:: python
    :linenos:

    import logging

    import pygram
    from pygram.ext import commands

    logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
    logger = logging.getLogger("pygram")

    bot = commands.Bot("token here")

    @bot.command()
    async def hi(ctx):
        await ctx.send("Hello")
        
    bot.run()


================  ========================================================================================================================================
Line number(s)    Description
================  ========================================================================================================================================
Lines 1-4         Import logging, pygram (telegram.py), and the pygram commands extension
Lines 6-7         Configure basic logging to get updates in console
Line 9            Create a ``commands.Bot`` instance with a token (get a token from `BotFather <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_)
Line 11-12        Define and add a command to our bot called 'hi'
Line 13           Send a greeting message to the chat where the command was invoked
Line 15           Start the bot (connects to Telegram and starts polling)
================  ========================================================================================================================================

.. _more examples:

More Examples
-------------

If you'd like to see more examples, take a look at the `examples folder <https://github.com/ilovetocode2019/telegram.py/tree/master/examples>`_ on GitHub.
