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

# TODO: move command registration from Bot.add_cog to CogMeta
# TODO: add properties like Cog.commands to Cog


class CogMeta(type):
    """Metaclass for Cog"""

    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        attrs["__cog_name__"] = kwargs.pop("name", name)

        new_cls = super().__new__(cls, name, bases, attrs, **kwargs)

        return new_cls


class Cog(metaclass=CogMeta):
    """Base cog class"""

    @property
    def qualified_name(self):
        """:class:`str`: The cog's name"""
        return self.__cog_name__

    @classmethod
    def listener(cls, name: str = None):
        """
        Makes a method in a cog a listener

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the event to register the function as
        """

        def deco(func):
            func._cog_listener = name or func.__name__
            return func

        return deco
