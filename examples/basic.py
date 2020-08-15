import logging

import pygram
from pygram.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("pygram")

# Make sure never to share your token
bot = commands.Bot("token here")

# Create and register a simple command called "hi".
# This is invoked with "/hi"
# and will make the bot reply with "Hello"
@bot.command()
async def hi(ctx):
    await ctx.send("Hello")

bot.run()
