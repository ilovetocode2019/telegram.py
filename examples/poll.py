import pygram
import logging

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("pygram")

bot = pygram.Bot("token here")

@bot.command(name="poll")
async def send(ctx):
    await ctx.send_poll(question="What is your favorite pet?", options=["Dogs", "Cats"])

@bot.event
async def on_poll(poll):
    #This runs when a poll updates or a poll is created
    #You can use this to collect poll answers
    #A poll class is automaticly passed in

    pass
    
bot.run()