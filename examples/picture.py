import io
import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S"
)
logger = logging.getLogger("telegrampy")

bot = commands.Bot("token here")


@bot.command(name="image")
async def image_command(ctx: commands.Context):
    # First, let's update the bot's status to say it's uploading a photo
    # Telegram users will see this in the client UI while the bot uploads the photo
    async with ctx.action("upload_photo"):
        # Now we'll open an image feed it into a buffer
        with open("/path/to/image", "rb") as file:
            content = file.read()
            photo = io.BytesIO(content)

        # Finally, we'll send our image to the chat alongside a caption
        await ctx.send_photo(photo, filename="photo.png", caption="This is a photo")


bot.run()
