<p align="center">
<img src="https://raw.githubusercontent.com/ilovetocode2019/telegram.py/master/docs/icon.png" alt="Logo" title="telegram.py" height="200" width="200"/>
</p>

# telegram.py

[![PyPI](https://img.shields.io/pypi/v/telegram.py)](https://pypi.org/project/telegram.py)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram.py)](https://pypi.org/project/telegram.py)
[![Documentation Status](https://readthedocs.org/projects/telegrampy/badge/?version=latest)](https://telegrampy.readthedocs.io/en/latest/?badge=latest)
[![GitHub - License](https://img.shields.io/github/license/ilovetocode2019/telegram.py)](LICENSE)
[![Telegram Channel](https://img.shields.io/badge/telegram-t.me%2Ftpy__updates-0088cc)](https://t.me/tpy_updates)

An async API wrapper for Telegram in Python

## Installation

Python 3.7+ is **required** to install and use telegram.py.

Install the latest release from PyPI:

```bash
# Mac/Linux
python3 -m pip install telegram.py

# Windows
py -3 -m pip install telegram.py
```

Or install the development version from GitHub:

```
# Mac/Linux
python3 -m pip install git+https://github.com/ilovetocode2019/telegram.py

# Windows
py -3 -m pip install git+https://github.com/ilovetocode2019/telegram.py
```

## Quick Example

```python
import logging

import telegrampy
from telegrampy.ext import commands

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger("telegrampy")

bot = commands.Bot("token here")

@bot.command()
async def hi(ctx):
    await ctx.send("Hello")

bot.run()
```

For a line-by-line walkthrough for this example, see the [quickstart](https://telegrampy.readthedocs.io/en/latest/quickstart.html#basic-example).

## Documentation

[Documentation can be found here.](https://telegrampy.readthedocs.io)
