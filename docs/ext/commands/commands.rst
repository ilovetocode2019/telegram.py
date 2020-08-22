.. currentmodule:: telegrampy

.. _ext_commands_commands:

Introduction to Commands
========================

Defining Commands
~~~~~~~~~~~~~~~~~

To define a command, simply use the :func:`telegrampy.ext.commands.Bot.command`
decorator on a coroutine. The coroutine's name will be the command's name.

Alternatively, you can define a command with the :func:`telegrampy.ext.commands.command`
decorator and add it to the bot with the :meth:`telegrampy.ext.commands.Bot.add_command` method.

.. code-block:: python

    import telegrampy
    from telegrampy.ext import commands

    bot = commands.Bot("token here")

    @bot.command()
    async def hi(ctx):
        await ctx.send("Hello!")

    bot.run()

With the above code, a user would invoke the command with ``/hi``,
and the bot would respond with ``Hello!``.

Each command must have at least one parameter, ``ctx``,
which is a :class:`telegrampy.ext.commands.Context` object.

In the case that the command name must be different from the coroutine name,
you can use the ``name`` kwarg in :func:`telegrampy.ext.commands.command`.
For a full list of parameters, see :class:`telegrampy.ext.commands.Command`.

Using Arguments
~~~~~~~~~~~~~~~

If you need to collect input from the user, you'll want to
use arguments.

Positional Arguments
--------------------

.. code-block:: python

    @bot.command()
    async def test(ctx, arg):
        await ctx.send(arg)

How does this translate in Telegram?

.. code-block:: none

    User: /test hi
    Bot : hi

Quite simply, the bot repeats the first word after the command.

.. warning::

    Please note that you will only get the first word
    using this method, as shown below.

.. code-block:: none

    User: /test hi there
    Bot : hi

Because of the way python works, you can have as many
positional arguments as you want.

For example:

.. code-block:: python

    @bot.command()
    async def test(ctx, arg1, arg2):
        await ctx.send(f"Arg1 is {arg1} and arg2 is {arg2}.")

The following is a layout of sections we have yet to write.

Keyword Arguments
-----------------

Description and an example for keyword arguments, or "consume rest".

Extras
------

Extras will include a list of args, like ``*args``.

Using Converters
~~~~~~~~~~~~~~~~

Description on what a converter is and why they're useful

Basic Converters
----------------

Advanced and Custom Converters
------------------------------
