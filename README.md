# SimpleInstagramManagerBot

This library allows you to like certain instagram photos by a list of hashtags or usernames.

## Installing ##

First of all you must have a telegram api key. 
 
Then copy the file `config.ini.dist` to `config.ini` and put your key there.

For docker user simple run:

    $ docker-compose up --build
    
For non docker user you need to install some dependencies. First is [Python Telegram Bot library](https://github.com/python-telegram-bot/python-telegram-bot):

    $ pip install python-telegram-bot --upgrade
    
And the second is First is [Instabot library](https://github.com/instagrambot/instabot):

    $ pip install -U instabot