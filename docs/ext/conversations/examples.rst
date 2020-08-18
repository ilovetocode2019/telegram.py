Examples
========

A Basic Conversation
--------------------

.. code-block:: python

    class BasicConversation(conversations.Conversation):
        @conversations.question("What's your name?", starting_question=True)
        async def name_question(self, message):
            self.name = message.content
            await self.ask(self.fav_color_question)

        @conversations.question("Okay, what's your favorite color?")
        async def fav_color_question(self, message):
            self.fav_color = message.content
            await self.chat.send(f"Alright!\nSo your name is {self.name}, and your favorite color is {self.fav_color}. Cool!")
            await self.stop()


    # Somewhere else...
    convo = BasicConversation()
    await convo.start(ctx.message, client=ctx.bot)

This conversation only asks two questions. It asks the name of the user and the user's
favorite color. When the conversation is done, it repeats what the user said.

A Setup Conversation
--------------------

.. code-block:: python

    class SetupConversation(conversations.Conversation):
        def __init__(self):
            super().__init__(timeout=120.0)

        @conversations.question("What is your email address?", starting_question=True)
        async def email_question(self, message):
            self.email = message.content
            await self.ask(self.name_question)

        @conversations.question("What would you like to be called?")
        async def name_question(self, message):
            self.name = message.content
            await self.stop()

        async def setup(self, message, *, client):
            await self.start(message, client=client, wait=True)
            return self.name, self.email


    # Somewhere else...
    convo = SetupConversation()
    name, email = await convo.setup(ctx.message, client=ctx.bot)
    await ctx.send(f"Name: {name}\nEmail: {email}")

This example demonstrates how setup conversations can be created.
The bot can walk the user through a setup process and return the
information back to the caller.
