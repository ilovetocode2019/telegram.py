Changelog
==========

v1.0.0
------

New Feautures
~~~~~~~~~~~~~
- Add loop, process_unerad, and wait parameters constructor to :class:`telegrampy.Client`.
- Add options kwargs to :class:`telegrampy.ext.commands.Bot`.
- Add :attr:`telegrampy.Client.loop`.
- Add :meth:`telegrampy.Client.set_name` and :meth:`telegrampy.Client.set_description`.
- Add :meth:`telegrampy.ext.commands.Bot.sync`.
- Add :meth:`telegrampy.Chat.set_title` and :meth:`telegrampy.Chat.set_description`.
- Add :meth:`telegrampy.Message.pin`, :meth:`telegrampy.Message.unpin`, and :meth:`telegrampy.Chat.clear_pins`.
- Add :meth:`telegrampy.Chat.leave`.
- Add :py:mod:`telegrampy.ext.conversations`.
- Add :meth:`telegrampy.on_post`, :meth:`telegrampy.on_post_edit`, :meth:`telegrampy.on_member_update`, :meth:`telegrampy.on_poll`, and :meth:`telegrampy.on_poll_answer` event listeners.
- Add :class:`telegrampy.Poll` and :class:`telegrampy.PollAnswer`.
- Add :attr:`telegrampy.User.language_code`, :attr:`telegrampy.User.is_premium`.
- Add :attr:`telegrampy.User.added_to_attachment_menu`, :attr:`telegrampy.User.is_premium`, :attr:`telegrampy.User.can_join_groups`, :attr:`telegrampy.User.can_read_all_group_messages`, :attr:`telegrampy.User.supports_inline_queries`, :attr:`telegrampy.User.can_connect_to_business`, :attr:`telegrampy.User.has_main_web_app`.
- Add :class:`telegrampy.BadRequest` and :class:`telegrampy.ServerError`.
- Add :class:`telegrampy.ext.commands.ExpectedClosingQuote`, :class:`telegrampy.ext.commands.ArgumentParsingError`, and :class:`telegrampy.ext.commands.UserInputError`.
- Add :class:`telegrampy.ext.commands.ExtensionError`, :class:`telegrampy.ext.commands.NoEntryPointError`, and :class:`telegrampy.ext.commands.ExtensionFailed`.
- Add :class:`telegrampy.Chat.set_photo`.
- Add :class:`telegrampy.Messageable`, :class:`telegrampy.PartialChat`, and :class:`telegrampy.PartialMessage`
- Add :meth:`telegrampy.Client.get_partial_chat`, :meth:`telegrampy.PartialChat.get_partial_message`, and :meth:`telegrampy.Chat.get_partial_message`.
- Add :attr:`telegrampy.Chat.display_name`.

Other Changes
~~~~~~~~~~~~~
- More throrough logging throughout update handling.
- Add complete typehints to library.
- Only message entity commands will be processed. Certain use-cases may break.
- :meth:`telegrampy.Chat.get_member` should return :class:`telegrampy.Member` instead of :class:`telegrampy.User`
- Rename :meth:`telegrampy.Client.user` to :meth:`telegrampy.Client.get_me`
- Rename :meth:`telegrampy.Message.edit` to :meth:`telegrampy.Message.edit_content`
- Split :meth:`telegrampy.Message.send` into :meth:`telegrampy.Message.send_document` and :meth:`telegrampy.Message.send_photo`
- Remove :attr:`telegrampy.Chat.history`, :attr:`telegrampy.Client.messages` and :meth:`telegrampy.Chat.fetch_message`  because they go against the Telegram API design.
- Remove :attr:`telegrampy.Document` and :attr:`telegrampy.Photo` as they are no longer needed with the new seperated send functions.
- Remove :class:`telegrampy.TelegramObject` in favor of more functional abstract base classes.

Bux Fixes
~~~~~~~~~
Considering that previous versions were incomplete and experimental, there are too many too list here.
The vast majority of previously encountered bugs have been resolved in this version.

v0.3.1
------

New
~~~
- Add command and command_completion events
- Add a start method to Client
- Add start alias for help command

Bug Fixes
~~~~~~~~~
- Ignore commands directed at other bots (/command@OtherBot will not invoke @YourBot)

Other
~~~~~
- Better logging
- get_context is now async
- Improvements with error messages

v0.3.0
------

New
~~~
- Add a description attribute to Cog
- Add a username attribute to Chat
- Add a signature and clean_params to Command
- Add converters
- Raise CommandInvokeError when the command callback itself fails
- Better BadArgument errors
- Don't show hidden commands in the help menu

Bug Fixes
~~~~~~~~~
- Fix listeners not being added when a cog is loaded
- Remove listeners properly when a cog is removed
- Fix member and chat fetching raising 404 errors
- Fix bug in help command
- Don't run the default command error handler if a command_error listener is registered

v0.2.0
------

New
~~~
- Ratelimit and better error code handling
- Message deleting and editing

Bug Fixes
~~~~~~~~~
- Fix a few typos
