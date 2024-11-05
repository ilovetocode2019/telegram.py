"""
telegram.py: Telegram Bot API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An async API wrapper for the Telegram bot API in Python.

:copyright: (c) 2020-2021 ilovetocode
:license: MIT, see LICENSE for more details.
"""

__title__ = "telegrampy"
__author__ = "ilovetocode"
__license__ = "MIT"
__copyright__ = "Copyright 2020-2021 ilovetocode"
__version__ = "1.0.0a"

from collections import namedtuple

from . import utils
from .client import Client
from .errors import *
from .chat import Chat
from .user import User
from .message import Message
from .poll import *

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")

version_info: VersionInfo = VersionInfo(major=0, minor=4, micro=0, releaselevel="alpha", serial=0)
