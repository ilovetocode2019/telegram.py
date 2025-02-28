# This example showcases the more primitive telegrampy.Client
# For bots that respond to commands, it's recommended to use the commands extension:
# https://telegrampy.readthedocs.io/en/latest/ext/commands/index.html

import logging

import telegrampy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S"
)
logger = logging.getLogger("telegrampy")

client = telegrampy.Client("your token here")


# This client will respond to messages containing the word "foo"
@client.listen("on_message")
async def handle_message(message: telegrampy.Message):
    # IMPORTANT: Telegram bots do not receive all messages by default.
    # See this page for more info: https://core.telegram.org/bots/faq#what-messages-will-my-bot-get
    if message.content and "foo" in message.content:
        await message.chat.send("bar")


client.run()
