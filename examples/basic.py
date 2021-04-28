import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("telegrampy")

# Make sure to never share your token
bot = commands.Bot("token here")


# Create and register a simple command called "hi"
# This is invoked with "/hi" and the bot will respond with "Hello"
@bot.command()
async def hi(ctx):
    await ctx.send("Hello")

# Start polling updates from Telegram
bot.run()
