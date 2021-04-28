import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("telegrampy")


bot = commands.Bot("token here")


@bot.command(name="image")
async def image_command(ctx):
    # Send the action 'upload_photo'
    await ctx.send_action("upload_photo")

    # Open an image and send it to the chat
    with open("file path here", "rb") as photo:
        await ctx.send_photo(photo, filename="photo.png", capton="This is a photo")

bot.run()
