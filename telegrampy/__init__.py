"""
telegram.py: Telegram Bot API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A simple API wrapper for the Telegram Bot API.

:copyright: (c) 2020 ilovetocode
:license: MIT, see LICENSE for more details.
"""

__title__ = "telegrampy"
__author__ = "ilovetocode"
__license__ = "MIT"
__copyright__ = "Copyright 2020 ilovetocode"
__version__ = "0.2.1a"

from collections import namedtuple

from . import utils
from .client import Client
from .errors import *
from .chat import Chat
from .user import User
from .message import Message
from .file import *
from .poll import Poll

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")

version_info = VersionInfo(major=0, minor=2, micro=0, releaselevel="final", serial=0)
