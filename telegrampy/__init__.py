"""
telegram.py: Telegram Bot API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An async API wrapper for the Telegram bot API in Python.

:copyright: (c) 2020-2024 ilovetocode
:license: MIT, see LICENSE for more details.
"""

__title__ = "telegrampy"
__author__ = "ilovetocode"
__license__ = "MIT"
__copyright__ = "Copyright 2020-2024 ilovetocode"
__version__ = "1.0.0a"

from collections import namedtuple

from . import utils
from .abc import TelegramObject, TelegramID
from .chat import Chat
from .client import Client
from .errors import *
from .member import Member, MemberUpdated
from .message import Message
from .poll import Poll, PollAnswer
from .user import User

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")

version_info: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel="alpha", serial=0)
