from __future__ import annotations

import functools
import inspect
import itertools
import os
import sys
import traceback
from typing import TYPE_CHECKING, Any, Awaitable, Callable, ClassVar, Coroutine, Dict, List, Optional, TypeVar, Union

from .chat import Chat
from .message import PartialMessage, Message
from .user import User

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types.keyboard import CallbackQuery as CallbackQueryPayload

    KeyboardT = TypeVar("KeyboardT", bound="InlineKeyboard")
    InlineKeyboardCallbackType = Callable[[KeyboardT, "CallbackQuery", "InlineKeyboardButton"], Awaitable[Any]]

    T = TypeVar("T")
    Coro = Coroutine[Any, Any, T]
    CoroFunc = Callable[..., Coro[T]]


class InlineKeyboard:
    """Represents an inline keyboard that appears as buttons on the message it is sent in."""

    __inline_keyboard_callbacks__: ClassVar[List[InlineKeyboardCallbackType]]

    def __init_subclass__(cls) -> None:
        cls.__inline_keyboard_callbacks__ = []

        for base in cls.__mro__:
            for value in base.__dict__.values():
                if getattr(value, "__inline_keyboard_button__", False) is True:
                    cls.__inline_keyboard_callbacks__.append(value)

    def __init__(self):
        self._stopped = False
        self._stop_callback: Optional[Callable[[], None]] = None
        self._buttons: List[InlineKeyboardButton] = []

        for callback in self.__inline_keyboard_callbacks__:
            button = InlineKeyboardButton(**callback.__inline_keyboard_button_kwargs__) # type: ignore
            button.callback = InlineKeyboardCallbackWrapper(callback, self, button) # type: ignore
            button._keyboard = self
            self._buttons.append(button)

    def add_button(self, button: InlineKeyboardButton) -> None:
        """Removes a button from the keyboard."""

        button._keyboard = self
        self._buttons.append(button)

    def remove_button(self, button: InlineKeyboardButton) -> None:
        """Adds a button to the keyboard."""

        self._buttons.remove(button)

    def stop(self) -> None:
        """Stops dispatching callback queries to this keyboard."""

        self._stopped = True
        if self._stop_callback is not None:
            self._stop_callback()
            self._stop_callback = None

    @property
    def stopped(self) -> bool:
        """:class:`bool` Whether the view has been stopped."""
        return self._stopped

    @property
    def active(self) -> bool:
        """:class:`bool` Whether the view is currently receiving callbacks."""
        return self._stop_callback is not None

    async def on_error(self, query: CallbackQuery, error: Exception, button: InlineKeyboardButton) -> None:
        """|coro|

        Called when a button inside the inline keyboard experiences an unhandled exception.

        Paramaters
        ----------
        query: Optional[:class:`.CallbackQuery`]
            The callback query that triggered the button callback.
        error: Optional[:class:`.Exception`]
            The exception that was raised.
        button: Optional[:class:`InlineKeyboardButton`]
            The button associated with the callback query.
        """

        print(f"Ignoring exception in inline keyboard for button {button}:", file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    async def _call_button(self, button: InlineKeyboardButton, query: CallbackQuery) -> None:
        try:
            await button.callback(query)
        except Exception as exc:
            await self.on_error(query, exc, button)

    @property
    def buttons(self) -> List[InlineKeyboardButton]:
        """List[:class:`InlineKeyboardButton`]: The list of buttons added to the inline keyboard."""
        return self._buttons.copy()

    def to_reply_markup(self) -> Dict[str, Any]:
        rows = []
        for key, buttons in itertools.groupby(self._buttons, key=lambda button: button.row or 0):
            rows.append([button.to_reply_markup_dict() for button in buttons])
        return {"inline_keyboard": rows}


class InlineKeyboardCallbackWrapper:
    def __init__(
        self,
        callback: InlineKeyboardCallbackType,
        keyboard: InlineKeyboard,
        button: InlineKeyboardButton
    ):
        self.callback: InlineKeyboardCallbackType = callback
        self.keyboard: InlineKeyboard = keyboard
        self.button: InlineKeyboardButton = button

    def __call__(self, query: CallbackQuery) -> Awaitable[Any]:
        return self.callback(self.keyboard, query, self.button)


class InlineKeyboardButton:
    """Represents a button that can be added to an :class:`.InlineKeyboard`.

    Parameters
    ----------
    text: :class:`str`
        The label of the button.
    url: Optional[:class:`str`]
        The HTTP or tg:// URL to be opened upon clicking the button.
    data: Optional[:class:`str`]
        A unique piece of data to identify the button in a callback query. Only for buttons without a URL.
    row: Optional[:class:`int`]
        The row to show the button on inside of the keyboard.

    Attributes
    ----------
    row: Optional[:class:`int`]
        The row to show the button on inside of the keyboard.
    """

    def __init__(
        self,
        *,
        text: str,
        url: Optional[str] = None,
        data: Optional[str] = None,
        row: Optional[int] = None,
    ):
        self.text: str = text
        self.url: Optional[str] = url

        if data is None and url is None:
            self.data: Optional[str] = os.urandom(16).hex()
        else:
            self.data: Optional[str] = data

        self.row: Optional[int] = row
        self._keyboard: Optional[InlineKeyboard] = None

    async def callback(self, query: CallbackQuery) -> None:
        """|coro|

        Called when the button is clicked. This should be implemented by subclasses.

        Parameters
        ----------
        query: :class:`.CallbackQuery`
            The callback query that triggered the button.
        """

        pass

    @property
    def keyboard(self) -> Optional[InlineKeyboard]:
        """Optional[InlineKeyboard]: The inline keyboard that the button belongs to."""
        return self._keyboard

    def to_reply_markup_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"text": self.text}

        if self.url is not None:
            data["url"] = self.url
        elif self.data is not None:
            data["callback_data"] = self.data

        return data


class CallbackQuery:
    """A callback query triggered by a button on an inline keyboard.

    Paramaters
    ----------
    id: :class:`str`
        The ID of the callback query
    user: :class:`.User`
        The user who sent the callback query.
    message: Optional[:class:`.PartialMessage`]
        The message containing the button that originated the query, if sent by the bot.
    inline_message_id: Optional[:class:`str`]
        The ID of the message sent by the through in inline mode that originated the query.
    chat_instance: :class:`str`
        Global unique ID for the chat which the message with the button was sent in.
    data: Optional[:class:`str`]
        The data associated with the button that triggered the query.
    game_short_name: Optional[:class:`str`]
        The short name of the game to be returned, serving as a unique ID.
    """

    def __init__(self, http: HTTPClient, data: CallbackQueryPayload):
        self._http: HTTPClient = http
        self.id: str = data["id"]
        self.user: User = User(http, data["from"])

        self.message: Optional[Union[PartialMessage, Message]] = PartialMessage(
            data["message"]["message_id"],
            Chat(http, data["message"]["chat"])
        ) if "message" in data else None

        self.inline_message_id: Optional[str] = data.get("inline_message_id")
        self.chat_instance: str = data["chat_instance"]
        self.data: Optional[str] = data.get("data")
        self.game_short_name: Optional[str] = data.get("game_short_name")


    async def answer(
        self,
        *,
        text: Optional[str] = None,
        show_alert: bool = False,
        url: Optional[str] = None,
        cache_time: int = 0
    ) -> None:
        """|coro|

        Responds to a callback query.
        The answer will be displayed to the user as notification at the top of their screen or as an alert.

        Paramaters
        ----------
        text: :class:`str`
            The text that will be shown to the user. If not passed, nothing will be shown to the user.
        show_alert: :class:`bool`
            Whether to show an alert instead of a notification at the top of the screen to the user.
        url: :class:`bool`
            Specifies the URL that opens your game for callback games buttons.
            Otherwise the link must be a t.me link that opens your bot with a specific parameter.
        cache_time: :class:`int`
            The amount of time the callback query may be cached client side.
        """

        await self._http.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time
        )


class InlineKeyboardState:
    def __init__(self, http: HTTPClient):
        self._http: HTTPClient = http
        self._keyboards: Dict[int, InlineKeyboard] = {}

    def add(self, message_id: int, keyboard: InlineKeyboard) -> None:
        keyboard._stop_callback = functools.partial(self.remove, message_id)
        self._keyboards[message_id] = keyboard

    def remove(self, message_id: int) -> None:
        del self._keyboards[message_id]

    def dispatch(self, query: CallbackQuery):
        if query.message is None:
            return

        inline_keyboard = self._keyboards.get(query.message.id)

        if inline_keyboard is None:
            return

        for button in inline_keyboard.buttons:
            if button.data == query.data:
                coro = inline_keyboard._call_button(button, query)
                self._http.loop.create_task(coro)


def inline_keyboard_button(**kwargs: Any) -> Callable[[InlineKeyboardCallbackType], InlineKeyboardCallbackType]:
    """Creates a button inside of an :class:`.InlineKeyboard` class, by using the decorated function as the callback.

    The wrapped function should take three positional parameters:
    the current instance of the :class:`.InlineKeyboard`, the :class:`.CallbackQuery` that triggered the button,
    and the :class:`.InlineKeyboardButton` being pressed.

    Parameters
    ----------
    kwargs:
        The kwargs to pass into the constructor when added to the :class:`.InlineKeyboard` instance.
    """


    def deco(func: InlineKeyboardCallbackType) -> InlineKeyboardCallbackType:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Button callback is not a coroutine.")

        func.__inline_keyboard_button__ = True # type: ignore
        func.__inline_keyboard_button_kwargs__ = kwargs # type: ignore
        return func

    return deco


class ReplyKeyboard:
    """Represents a custom keyboard with reply options that is shown to a user.

    Parameters
    ----------
    persistent: :class:`bool`
        Whether the keyboard should always be shown.
    resize: :class:`bool`
        Whether clients should shrink/expand the keyboard to fit the buttons more optimially.
        If ``False``, the keyboard will always take up the same amount of space as the standard keyboard.
    one_time: :class:`bool`
        Whether to close the keyboard after using it. Users will still be able to upon it up later.
    placeholder: :class:`bool`
        The placeholder to show in the input field when the keyboard is active.
    selective: :class:`bool`
        Whether to target all users in the chat or specific users.
        If selective, the markup will only be applied to users mentioned in the message and the author of the reply message.
    """

    def __init__(
        self,
        *,
        persistent: bool = False,
        resize: bool = False,
        one_time: bool = False,
        input_placeholder: Optional[str] = None,
        selective: bool = False
    ):
        self._buttons: List[ReplyKeyboardButton] = []
        self.persistent: bool = persistent
        self.resize: bool = resize
        self.one_time: bool = one_time
        self.input_placeholder: Optional[str] = input_placeholder
        self.selective: bool = selective

    def add_button(self, button: ReplyKeyboardButton) -> None:
        self._buttons.append(button)

    def remove_button(self, button: ReplyKeyboardButton) -> None:
        self._buttons.remove(button)

    @property
    def buttons(self) -> List[ReplyKeyboardButton]:
        """List[:class:`.ReplyKeyboardButton`]: The list of buttons added to the reply keyboard."""
        return self._buttons.copy()

    def to_reply_markup(self) -> Dict[str, Any]:
        rows = []
        for key, buttons in itertools.groupby(self._buttons, key=lambda button: button.row or 0):
            rows.append([button.to_reply_markup_dict() for button in buttons])

        data = {
            "keyboard": rows,
            "is_persistent": self.persistent,
            "resize_keyboard": self.resize,
            "one_time_keyboard": self.one_time,
            "selective": self.selective,
        }

        if self.input_placeholder is not None:
            data["input_field_placeholder"] = self.input_placeholder

        return data

class ReplyKeyboardButton:
    """Represents a button that can be added to a reply keyboard.

    text: :class:`str`
        The label of the button.
    row: Optional[:class:`int`]
        The row to show the button on inside of the keyboard.

    Attributes
    ----------
    row: Optional[:class:`int`]
       The row to show the button on inside of the keyboard.
    """

    def __init__(self, *, text: str, row: Optional[int] = None):
        self.text: str = text
        self.row: Optional[int] = row

    def to_reply_markup_dict(self) -> Dict[str, Any]:
        return {"text": self.text}


class ReplyKeyboardRemove:
    """Removes a reply keyboard from the chat when sent as a reply markup.

    Parameters
    ----------
    selective: :class:`bool`
        Whether to target all users in the chat or specific users.
        If selective, the markup will only be applied to users mentioned in the message and the author of the reply message.
    """

    def __init__(self, selective: bool = False):
        self.selective: bool = selective

    def to_reply_markup(self) -> Dict[str, Any]:
        return {"remove_keyboard": True, "selective": self.selective}


class ForceReply:
    """Populates a reply interface in the chat when sent as a reply markup.

    Parameters
    ----------
    placeholder: Optional[:class:`str`]
        The placeholder that will be shown in the input field when the reply interface is active.
    selective: :class:`bool`
        Whether to target all users in the chat or specific users.
        If selective, the markup will only be applied to users mentioned in the message and the author of the reply message.
    """

    def __init__(self, *, placeholder: Optional[str] = None, selective: bool = False):
        self.placeholder: Optional[str] = placeholder
        self.selective: bool = selective

    def to_reply_markup(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"force_reply": True, "selective": self.selective}

        if self.placeholder is not None:
            data["input_field_placeholder"] = self.placeholder

        return data
