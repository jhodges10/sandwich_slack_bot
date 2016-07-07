# sandwich_slack_bot

This readme doesn't have a ton of information in it for now.

Basically this new version of the slackbot is designed to split the listening part of the real-time-messaging Slack API into an asynchronous thread.

On top of that - this should allow us to encode multiple clips at a time, save user preference for clips at 540 or 1080, answer simple questions from a CSV file using fuzzy matching and anything else we decide to add.

encode_bot_v.98 is the current working version that we use today

encode_bot_combined is the version that I'm working on currently with pipes to stdout. It will also contains the User class object that is instantiated when they first communicate with the script (might save this to a separate CSV)

