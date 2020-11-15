"""
MIT License

Copyright (c) 2020 ilovetocode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .errors import BadArgument
from telegrampy.chat import Chat
from telegrampy.user import User
from telegrampy.errors import HTTPException

class Converter:
    """
    Base class for converters.
    """

    async def convert(self, ctx, arg):
        """
        Does the converting.
        """
        raise NotImplementedError

class UserConverter(Converter):
    """
    Converts an argument into a user.
    """

    async def convert(self, ctx, arg):
        try:
            arg = int(arg)
        except ValueError:
            raise BadArgument(arg, User, "Argument is not an ID")
        try:
            return await ctx.chat.get_member(arg)
        except HTTPException:
            raise BadArgument(arg, User, "Failed to fetch user")

class ChatConverter(Converter):
    """
    Converts an argument into a chat.
    """

    async def convert(self, ctx, arg):
        try:
            arg = int(arg)
        except ValueError:
            raise BadArgument(arg, Chat, "Argument is not an ID")
        try:
            return await ctx.bot.get_chat(arg)
        except HTTPException:
            raise BadArgument(arg, Chat, "Failed to fetch chat")
