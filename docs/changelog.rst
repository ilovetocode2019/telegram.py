Changelog
==========

v0.3.1
------

New
~~~
- Add command and command_completion events
- Add a start method to Client
- Add start alias for help command

Bug Fixes
~~~~~~~~~
- Ignore commands directed at other bots

Other
~~~~~
- Better logging
- get_context is now async
- Improvments with error messages

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
