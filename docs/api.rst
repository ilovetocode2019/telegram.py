.. currentmodule:: telegrampy

API Reference
=============

Client
------

.. autoclass:: Client
    :members:

Events
~~~~~~

.. function:: on_message(message: telegrampy.Message)

    Called when a message is sent.

.. function:: on_message_edit(message: telegrampy.Message)

    Called when a message is edited.

.. function:: on_post(message: telegrampy.Message)

    Called when a channel post is sent.

.. function:: on_post_edit(message: telegrampy.Message)

    Called when a channel post is edited.

.. function:: on_callback_query(query: telegrampy.CallbackQuery)

    Called when a callback query is received from an inline keyboard button.
    Instead of trying to handle callbacks yourself, consider using :class:`.InlineKeyboard`, which handles this for you.

.. function:: on_member_update(member_update: telegrampy.MemberUpdated)

    Called when a chat member is updated.

.. function:: on_poll(poll: telegrampy.Poll)

    Called when a poll is sent.

.. function:: on_poll_answer(answer: telegrampy.PollAnswer)

    Called when someone answers a non-anonymous poll.

.. function:: on_error(error)

    Called when an error occurs within an event handler.

Utilities
---------

.. autofunction:: telegrampy.utils.escape_markdown


Telegram Models
---------------

Base
~~~~

.. autoclass:: Messageable()
    :members:

Chat
~~~~

.. autoclass:: PartialChat()
    :members:
    :inherited-members:

.. autoclass:: Chat()
    :members:
    :inherited-members:

.. autoclass:: ChatInvite()
    :members:

Message
~~~~~~~

.. autoclass:: PartialMessage
    :members:
    :inherited-members:

.. autoclass:: Message()
    :members:
    :inherited-members:

.. autoclass:: MessageEntity()
    :members:

User
~~~~

.. autoclass:: User()
    :members:

.. autoclass:: ClientUser()
    :members:

.. autoclass:: UserProfilePhotos()
    :members:

Member
~~~~~~

.. autoclass:: Member()
    :members:
    :inherited-members:

.. autoclass:: MemberUpdated()
    :members:

Poll
~~~~

.. autoclass:: Poll()
    :members:

.. autoclass:: PollAnswer()
    :members:

Files
-----

.. autoclass:: File()
    :members:

.. autoclass:: PhotoSize()
    :members:

Markup
~~~~~~

.. autoclass:: InlineKeyboard
    :members:

.. autoclass:: InlineKeyboardButton
    :members:

.. autofunction:: inline_keyboard_button
    :decorator:

.. autoclass:: ReplyKeyboard
    :members:

.. autoclass:: ReplyKeyboardButton
    :members:

.. autoclass:: ReplyKeyboardRemove
    :members:

.. autoclass:: ForceReply
    :members:

.. autoclass:: CallbackQuery
    :members:


Exceptions
----------

.. autoclass:: TelegramException
    :members:

.. autoclass:: HTTPException
    :members:

.. autoclass:: BadRequest
    :members:

.. autoclass:: InvalidToken
    :members:

.. autoclass:: Forbidden
    :members:

.. autoclass:: Conflict
    :members:

.. autoclass:: ServerError
    :members:
