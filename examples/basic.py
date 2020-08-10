import pygram
import logging

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("pygram")

bot = pygram.Bot("token here")

@bot.command(name="hi")
async def send(ctx):
    await ctx.send("Hello")
    
bot.run()