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

Converters can be usefull if you need to convert an argument to an object.
For example you may have a command that needs to take an argument as a :class:`telegrampy.User`.

Basic Converters
----------------

A basic converterer is a callable that takes an argument and returns an object or variable.
For example, if you wanted to make a command that added two numbers you could use the integer converter.


.. code-block:: python

    @bot.command()
    async def add(ctx, a: int, b: int):
        await ctx.send(a+b)

Since any callable can be used as a converter, you can make your own converter with a function.

.. code-block:: python

    def codeblock(arg):
        return f"`{arg}`"

    @bot.command(name="codeblock")
    async def codeblock_command(ctx, code: codeblock):
        await ctx.send(code)

Advanced and Custom Converters
------------------------------

Sometimes basic converters may not work for our needs. For example, We may need to get more context on the command invocation or do something async.
That's what a :class:`telegrampy.ext.commands.Converter` is for.

We can use a builtin :class:`telegrampy.ext.commands.Converter` like this. Telegram.py will see that user should be passed in as a user object and then use the :class:`telegrampy.ext.commands.UserConverter` to convert it.

.. code-block:: python

    @bot.command()
    async def dm(ctx, user: telegrampy.User):
        await user.send("Hello!")

If we want to make a custom converter we can do this.

.. code-block:: python

    class CommandConverter(commands.Converter):
        async def convert(self, ctx, arg):
            command = ctx.get_command(arg)
            if not command:
                raise commands.BadArgument(arg, commands.Command, f"Could not find a command named '{arg}'")
            return command

    @bot.command(name="info", description="Get info on a command")
    async def info(ctx, command: CommandConverter):
        await ctx.send(f"{command.name}: {command.description}")
