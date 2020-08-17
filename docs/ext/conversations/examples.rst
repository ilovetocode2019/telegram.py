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


    # Elsewhere
    convo = BasicConversation()
    await convo.start(ctx.message, client=ctx.bot)

This conversation only asks two questions. It asks the name of the user and the user's
favorite color. When the conversation is done, it repeats what the user said.
