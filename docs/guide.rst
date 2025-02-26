.. currentmodule:: telegrampy

Guide
========

Basic Usage
-----------

.. code-block:: python

    import telegrampy

    client = telegrampy.Client("token here")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        elif message.content == client.user.mention:
            await message.chat.send(f"\N{WAVING HAND SIGN} Hello {message.author.mention}!")

    bot.run()

Commands Extensions
-------------------

Introduction
~~~~~~~~~~~~

Checks
~~~~~~

User Input
~~~~~~~~~~

Cogs
~~~~

Extensions
~~~~~~~~~~
