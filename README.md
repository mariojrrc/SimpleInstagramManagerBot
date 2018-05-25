# SimpleInstagramManagerBot

This library allows you to like certain instagram photos by a list of hashtags.
It also, likes your timeline feed and like the last 3 media of your last likers.

[Check it here](https://t.me/@SimpleInstaManagerBot)

## Installing ##

First of all you must have a telegram api key and python 3 installed. 
 
Then you put your telegram bot key within the `.env`.

For docker user simple run:

    $ docker-compose up --build
    
For non docker user you need to install some dependencies. They most important are [Python Telegram Bot library](https://github.com/python-telegram-bot/python-telegram-bot) and [Instabot library](https://github.com/instagrambot/instabot). To install those you can use the following command:

    $ pip install -r requirements.txt -U

Then you run:

    $ python main.py

## TODO ##

- Add translation to English
- Receive params of amount to like medias (default is 10)