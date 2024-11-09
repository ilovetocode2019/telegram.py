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

.. function:: on_inline_query(message: telegrampy.Message)

    Called when an inline query is received.

.. function:: on_member_update(member_update: telegrampy.MemberUpdated)

    Called when a chat member is updated.

.. function:: on_poll(poll: telegrampy.Poll)

    Called when a poll is created.

.. function:: on_poll_answer(answer: telegrampy.PollAnswer)

    Called when someone answers a non-anonymous poll.

.. function: 

.. function:: on_error(error)

    Called when an error occurs.

Utilities
---------

.. autofunction:: telegrampy.utils.escape_markdown


Telegram Models
---------------

Base
~~~~
.. autoclass:: TelegramID
    :members:

Message
~~~~~~~

.. autoclass:: Message()
    :members:

User
~~~~

.. autoclass:: User()
    :members:

Chat
~~~~

.. autoclass:: Chat()
    :members:

Member
~~~~~~

.. autoclass:: Member
    :members:

.. autoclass:: MemberUpdated
    :members:

Inline
~~~~~~

.. autoclass:: InlineQuery
    :members:

.. autoclass:: InlineQueryResults
    :members:

.. autoclass:: InlineQueryResultsButton
    :members:

Location
~~~~~~~~

.. autoclass:: Location

Poll
~~~~

.. autoclass:: Poll()
    :members:

.. autoclass:: PollAnswer()
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
