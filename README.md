Hi,

This is my Gmail generator project from the summer of 2022. I worked on it for 3-4 months. At the time, I didn't know much about making the code elegant: dividing it into modules, adding comments, etc. It may be hard to jump right into it now, but I'm uploading it here to show that I worked on one (as of now for me) pretty big project.

The bot was pretty decent, with about 95%+ of tasks successfully completed. Note: we're talking about the process of registering the Gmail account, verifying it with a phone, setting up spam filters, and forwarding. It was able to complete around 30 tasks per hour.

Nevertheless, if anyone still wants to jump into the code, I highly recommend checking functions such as "create_accounts", "create_and_forward_gmails", or "create_master_gmail_profiles".

Modules:

- Register, verify with phone, set filters, and forward Gmail accounts
- Only create Gmail accounts
- Only forward Gmail accounts
- Create, open, and delete master Gmail Chrome profiles (master = the email address to which we forward all the other accounts)
- Check whether master accounts were clipped or not
- Connect to and check connection with a mobile device (see below)

Features:
- Phone verification using the sms-activate.org API, with the possibility to reuse the same phone number if possible
- Connect to an Android phone (<4.4.2 version) and use it as a "mobile proxy" for the tasks.
- Generate logs (see examples in log files)
- Work with logs and load them. In case of rerunning some tasks, depending on the state they were ended with, the bot would know what to do.
