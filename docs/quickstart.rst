Quickstart
============

Make sure to :doc:`install telegram.py </installation>` before proceeding!

.. _basic example:

Basic Example
---------------

To give you a taste of telegram.py, we'll go over a quick example line-by-line.

.. code-block:: python
    :linenos:

    import telegrampy
    from telegrampy.ext import commands

    bot = commands.Bot("token here")

    @bot.command()
    async def hi(ctx):
        await ctx.send("Hello!")

    bot.run()


* **Lines 1 and 2:** We first import telegram.py (named :code:`telegrampy`) and the telegram.py commands extension
* **Line 4:** Next, we create a ``commands.Bot`` instance with our bot token.
  You can get a bot token from `BotFather <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_.
* **Line 6-8:** Say we want to create a command called **/hi** that always responds with "Hello!".
  To do this, we create an :code:`async` function and use the :code:`@bot.command()` decorator to make
  it a command of our newly-created :code:`bot`.
  This function will get called whenever a user uses the /hi command of our bot.
  Finally, we can respond to the user's request by using :code:`await ctx.send("Hello!")`.
  This will send a message to whichever chat the command was used in.
* **Line 10:** Lastly, to start our bot so that it starts responding to commands,
  we use :code:`bot.run()`.


.. _adding_logging:

Adding Logging
---------------

telegram.py comes with some basic logging out-of-the-box to show when your bot
connects to Telegram or experiences errors.

Let's set up logging in Python to see these logs in our terminal.

.. code-block:: python
    :emphasize-lines: 1, 6, 7, 8, 9, 10

    import logging

    import telegrampy
    from telegrampy.ext import commands

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%d-%m %H:%M:%S"
    )

    bot = commands.Bot("token here")

    @bot.command()
    async def hi(ctx):
        await ctx.send("Hello!")

    bot.run()


.. _next_steps:

Next Steps
------------

Itching for more?

- **Tutorial:** Get to know more of telegram.py with the :doc:`tutorial </tutorial>`.
- **Guides:** Looking to do something specific? Browse the :doc:`guides </guides/index>`.
- **Examples:** Check out the `examples <https://github.com/ilovetocode2019/telegram.py/tree/master/examples>`_ on GitHub.
- **Help:** Are you stuck? Help is available in our `Telegram group <https://t.me/tpy_group>`_.
