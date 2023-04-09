# Fully-automated-Gmail-generator

Hi,

This was my Gmail generator project back in the summer 2022. I have been working on it for 3-4 months. At the time I didn't know that much about making the code elegant: dividing it into modules, add comments etc. It may be hard to jump right into it right now. I upload it here just to show that I have been working on one (as of now for me) pretty big project.

The bot was pretty decent, about 95%+ of the tasks used to be successful. Note: we are talking about the process of registering the gmail, verifying it with a phone, setting spam filter and forwarding. It used to make 30 that kind of tasks/per hour.

Nevertheless if anyone still would like to jump into the code i highly advice to check the functions such as: "create_accounts", "create_and_forward_gmails" or "create_master_gmail_profiles"

Modules:
- Register, verify, set filters and forward gmails
- Only create the gmails
- Only forward the gmails
- Create, open and delete master gmails chrome profiles (master = mail to which we forward all the rest.)
- Connect and check connection with a mobile device (read below)
- Checker whether masters were clipped or not

Additional features:
- Phone verification using sms-activate.org API. Additional possibility to reuse the same phone number if possible.
- Connecting to the android phone (<4.4.2 version) and using it as a "mobile proxy"
- Generating the logs and reusing them if needed
- A
