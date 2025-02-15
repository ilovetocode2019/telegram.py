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

from . import *
from .abc import  *
from .chat import *
from .client import *
from .errors import *
from .file import *
from .markup import *
from .member import *
from .message import *
from .poll import *
from .user import *

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")

version_info: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel="alpha", serial=0)
