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

    import pygram
    import logging

    logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
    logger = logging.getLogger("pygram")

    bot = pygram.Bot("token here")

    @bot.command()
    async def hi(ctx):
        await ctx.send("Hello")
        
    bot.run()


================  ==================================================================================================================================
Line number(s)    Description
================  ==================================================================================================================================
Lines 1-2         Import pygram (telegram.py) and logging
Lines 4-5         Configure basic logging to get updates in console
Line 7            Create a pygram.Bot instance with a token (get a token from `BotFather <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_)
Line 9-10         Define and add a command to our bot called 'hi'
Line 11           Send a greeting message to the chat where the command was invoked
Line 13           Start the bot (connects to Telegram and starts polling)
================  ==================================================================================================================================

.. _more examples:

More Examples
-------------

If you'd like to see more examples, take a look at the `examples folder <https://github.com/ilovetocode2019/telegram.py/tree/master/examples>`_ on GitHub.
