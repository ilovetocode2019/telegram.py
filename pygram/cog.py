class Cog:
    """Base cog class"""

    @classmethod
    def listener(cls, name: str=None):
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