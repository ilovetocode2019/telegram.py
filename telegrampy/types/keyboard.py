from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from .message import Message, InaccessibleMessage
    from .user import User

CallbackQuery = TypedDict(
    "CallbackQuery",
    {
        "id": str,
        "from": User,
        "message": NotRequired[Message | InaccessibleMessage],
        "inline_message_id": NotRequired[str],
        "chat_instance": str,
        "data": NotRequired[str],
        "game_short_name": NotRequired[str]
    }
)
