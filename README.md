# telegram.py

An async API wrapper for Telegram in Python

## Install

```bash
pip install git+https://github.com/ilovetocode2019/telegram.py
```

## Example

```python
import pygram
import logging

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("pygram")

bot = pygram.Bot("token here")

@bot.command(name="hi")
async def hi(ctx):
    await ctx.send("Hello")
    
bot.run()
```

## Documentation

Documentation can be found [here](https://telegrampy.readthedocs.io)
