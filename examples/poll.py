import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("telegrampy")

bot = commands.Bot("token here")


@bot.command()
async def poll(ctx):
    await ctx.send_poll(question="What is your favorite pet?", options=["Dogs", "Cats"])

bot.run()
