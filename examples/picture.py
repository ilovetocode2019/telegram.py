import pygram
import logging

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("pygram")

bot = pygram.Bot("token here")

@bot.command(name="image")
async def send(ctx):
    await ctx.send_action("typing")
    f = open("file path here", "rb")
    photo = pygram.Photo(file=f, caption="This is a photo")
    await ctx.send(file=photo)

bot.run()