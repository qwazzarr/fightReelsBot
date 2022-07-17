**FightReels Telegram Bot**
-
If you faced the problem that the only reason you continue to use instagram is 
for the sake of checking friends' stories, HOWEVER the devilish invention by the name of _REELS_ desperately tries 
to steel your time, THEN this bot is for you.

Libraries:
-
* pyTelegramBotAPI	v4.6.0 Telegram API library
* selenium	v4.3.0	To simulate user activity in Instagram
* sched . For scheduled stories checking.

* **Python** v.3.8

To start:
-
If you want to use the bot, you will need to create a `credentials.py` file and put it in the same directory 
as `botTelegram.py`. The file should hold 3 variables :
* `LOGIN` - your instagram login
* `PASSWORD` - your instagram password
* `TOKEN` - your Telegram Bot token you received from https://t.me/BotFather

The only thing that left is to start `botTelegram.py`

Usage:
- 
* /start To start the bot
* /help Help
* Follow to a new account -> Start tracking. 
* Default update frequency is 1 minute
