# coding=utf-8
import json

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from pathlib import Path
from dotenv import load_dotenv

import logging
import configparser
import os
from os.path import join, dirname

from ExtendedBot import ExtendedBot

# TODO create tests for this file

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# get token from '.env' file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

USERNAME, PASSWORD, LIKEBY, LIKEBYHASHTAGS, LIKEFEED, LIKELASTMEDIALIKERS = range(6)

USER_COOKIEFILE_SUFFIX = '_cookie.txt'
USER_HASHTAGFILE_SUFFIX = '_hashtags.txt'
USER_SKIPPEDFILE_SUFFIX = '_skipped.txt'
USER_UNFOLLOWEDFILE_SUFFIX = '_unfollowed.txt'
USER_WHITELISTFILE_SUFFIX = '_whitelist.txt'
USER_BLACKLISTFILE_SUFFIX = '_blacklist.txt'
USER_COMMENTSFILE_SUFFIX = '_comments.txt'
USER_FRIENDSFILE_SUFFIX = '_friends.txt'
USER_FOLLOWEDFILE_SUFFIX = '_followed.txt'

reply_keyboard_like_choice = [['sim', 'nao']]


def start(bot, update):
    # Reads cookie file to check if credentials are already stored
    user_file = Path(str(update.message.from_user.id) + USER_COOKIEFILE_SUFFIX)
    cookie_file_name = str(update.message.from_user.id) + USER_COOKIEFILE_SUFFIX
    if user_file.is_file():

        # Try to decode cookie data
        try:
            cookie = open(cookie_file_name, 'r')
            cookie_data = json.load(cookie)
        except Exception:
            # If it fails, removes the cookie file and starts chat again
            user_file.unlink()
            logger.info('Falha ao carregar o json do cookie usuario: %d', update.message.from_user.id)
            return start(bot, update)

        # If there is no required data, remove the cookie file and finishes chat
        if not cookie_data['ds_user'] or not cookie_data['sessionid']:
            update.message.reply_text(
                'username ou password não informado no cookie!')
            user_file.unlink()
            logger.info('credenciais nao definidas no cookie usuario: %d', update.message.from_user.id)
            return ConversationHandler.END

        # If the file is ok, show options to the user.
        update.message.reply_text('Bem vindo ao SimpleIntagramManager Bot! \nVi que suas credenciais já estão '
                                  'salvas!\nGostaria de curtir por hashtags?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True)
                                  )
        return LIKEBY

    # If credentials are not stored, asks for it. Username is asked first
    update.message.reply_text('Bem vindo ao SimpleIntagramManager Bot! \nPreciso de suas credenciais, qual nome de '
                              'usuário?')

    return USERNAME


def username(bot, update, user_data):
    # Receives credentials of username
    user = update.message.from_user
    user_data['username'] = update.message.text
    logger.info('username informado pelo %s é: %s', user.first_name, update.message.text)
    update.message.reply_text('Obrigado, agora preciso de sua senha de login.')

    # Redirect to ask password
    return PASSWORD


def password(bot, update, user_data):
    # Receives credentials of password
    user_data['password'] = update.message.text
    user = update.message.from_user
    logger.info('Senha informada pelo %s é: %s', user.first_name, update.message.text)
    update.message.reply_text(
        'Thanks! Gostaria de curtir por hashtags?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))

    # Redirect to ask by which method to like -> hashtag or username
    return LIKEBY


def likeby(bot, update, user_data):

    logger.info("Curtir por hashtag?: %s", update.message.text)

    # Check choice to like by hashtags
    if update.message.text == 'sim':
        update.message.reply_text('Pod crer! Informe as hashtags sem \'#\' e separada por espaços. Caso deseje utilizar'
                                  ' as últimas hashtags envie "recente".',
                                  reply_markup=ReplyKeyboardRemove())
        return LIKEBYHASHTAGS
    # Check choice to like by usernames. NOT IMPLEMENTED YET.
    elif update.message.text == 'nao':
        update.message.reply_text('Pod crer! Deseja curtir automaticamente seu feed?.',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        return LIKEFEED
    # If no choice, asks again
    else:
        update.message.reply_text('Não entendi, por favor repita.',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        return LIKEBY

def likefeed(bot, update, user_data):

    logger.info("Curtir o feed? %s", update.message.text)

    # Check choice to like feed
    if update.message.text == 'sim':
        instaBot = getBot(update, user_data)
        update.message.reply_text('Curtindo seu feed;', reply_markup=ReplyKeyboardRemove())
        instaBot.like_timeline()
        update.message.reply_text('Finalizado! Deseja curtir seus últimos likers?',
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        
        return LIKELASTMEDIALIKERS
    # Check choice to like by usernames. NOT IMPLEMENTED YET.
    elif update.message.text == 'nao':
        update.message.reply_text('Ok! Deseja curtir seus últimos likers?',
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        
        return LIKELASTMEDIALIKERS
    # If no choice, asks again
    else:
        update.message.reply_text('Não entendi, por favor repita.',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        return LIKEFEED

def likebyhashtags(bot, update, user_data):

    # Recent used hashtag file name
    hashtag_file_name = str(update.message.from_user.id) + USER_HASHTAGFILE_SUFFIX

    # Check if there the user want use stored hashtags
    if update.message.text == 'recente':

        # Check if file exists
        hashtag_file_path = Path(hashtag_file_name)

        if hashtag_file_path.is_file():

            # If so, read the file
            user_file = open(hashtag_file_name, 'r')
            tags = user_file.read().split(' ')

        else:
            # If not, show message e redirect to read hashtag by user's typing again
            update.message.reply_text('Nenhuma hashtag encontrada. Por favor, insira pelo menos uma hashtag.')
            return LIKEBYHASHTAGS
    else:
        # Reads hashtags input and save it in the file
        tags = update.message.text.split(' ')
        user_file = open(hashtag_file_name, 'w')
        user_file.write(update.message.text)

    # Start instagram bot
    bot = getBot(update, user_data)
    logger.info("Hashtags são: %s", "".join(tags))

    # Builds a task list to like by each hashtag
    tasks_list = []
    for item in tags:
        logger.info("adicionado task para #%s", item)
        tasks_list.append((bot.like_hashtag, {'hashtag': item, 'amount': 10}))

    # Executes the task list
    for func, arg in tasks_list:
        # Get hashtag and amount
        hashtag = arg['hashtag']
        amount = arg['amount']
        try:
            # Get total media to like
            total = bot.get_total_hashtag_medias(hashtag, amount)
            update.message.reply_text("Curtindo {} foto(s) com a hashtag #{}.".format(len(total), hashtag))

            # Executes the task
            func(**arg)
            update.message.reply_text("Finalizado curtida de fotos com hashtag #{}.".format(hashtag))

        # If error, show message and skip to next hashtag
        except Exception as e:
            logger.info(e.message)
            update.message.reply_text('Erro ao curtir a hashtag %s!' % hashtag)

    # When there is no more tast, show message and finishes chat
    update.message.reply_text('Finalizado! %d fotos foram curtidas!' % bot.total['likes'])

    update.message.reply_text('Deseja curtir seus feed?',
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))

    return LIKEFEED

def likelastmedialikers(bot, update, user_data):
    
    # Check choice to like feed
    if update.message.text == 'sim':
        instaBot = getBot(update, user_data)
        update.message.reply_text('Curtindo seus últimos likers;', reply_markup=ReplyKeyboardRemove())
        instaBot.like_your_feed_likers()
        update.message.reply_text('Finalizado! Até mais.', reply_markup=ReplyKeyboardRemove())
        
        return ConversationHandler.END
    # Check choice to like by usernames. NOT IMPLEMENTED YET.
    elif update.message.text == 'nao':
        update.message.reply_text('OK, até mais!', reply_markup=ReplyKeyboardRemove())
        
        return ConversationHandler.END
    # If no choice, asks again
    else:
        update.message.reply_text('Não entendi, por favor repita.',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard_like_choice, one_time_keyboard=True))
        return LIKELASTMEDIALIKERS

def getBot(update, user_data):
    
    # User cookie file name
    cookie_file_name = str(update.message.from_user.id) + USER_COOKIEFILE_SUFFIX

    whitelist_file = str(update.message.from_user.id) + USER_WHITELISTFILE_SUFFIX
    blacklist_file = str(update.message.from_user.id) + USER_BLACKLISTFILE_SUFFIX
    comments_file = str(update.message.from_user.id) + USER_COMMENTSFILE_SUFFIX
    followed_file = str(update.message.from_user.id) + USER_FOLLOWEDFILE_SUFFIX
    unfollowed_file = str(update.message.from_user.id) + USER_UNFOLLOWEDFILE_SUFFIX
    skipped_file = str(update.message.from_user.id) + USER_SKIPPEDFILE_SUFFIX
    friends_file = str(update.message.from_user.id) + USER_FRIENDSFILE_SUFFIX

    args = {'whitelist_file': whitelist_file, 'blacklist_file': blacklist_file,
            'comments_file': comments_file, 'followed_file': followed_file,
            'unfollowed_file': unfollowed_file, 'skipped_file': skipped_file,
            'friends_file': friends_file}

    instaBot = ExtendedBot(**args)

    # Check if there is cookie file stored
    # TODO refactor this verification
    user_file = Path(cookie_file_name)
    if user_file.is_file():
        # Try to decode cookie data
        try:
            cookie = open(cookie_file_name, 'r')
            cookie_data = json.load(cookie)
        except Exception:
            # If it fails, removes the cookie file and starts chat again
            user_file.unlink()
            logger.info('Falha ao carregar o json do cookie usuario: %d', update.message.from_user.id)
            return start(instaBot, update)

        if not cookie_data['ds_user'] or not cookie_data['sessionid']:
            update.message.reply_text(
                'username ou password não informado no cookie!')
            user_data.clear()
            return ConversationHandler.END

        # If the file is ok, build args to login
        args = {'username': cookie_data['ds_user'], 'password': cookie_data['sessionid'],
                'cookie_fname': cookie_file_name,}
    # If cookie not stored, get credentials by user_data the has been created throw the chat's workflow
    else:
        # If not exists credentials, show message and finishes the chat
        if not user_data['username'] or not user_data['password']:
            update.message.reply_text(
                'username ou password não informado!')
            user_data.clear()
            return ConversationHandler.END

        # If credentials are ok, build args to login
        args = {'username': user_data['username'], 'password': user_data['password'],
                'cookie_fname': cookie_file_name}

    # Attempt to login, if error show message e finishes conversation
    update.message.reply_text('Verificando login.')
    if not instaBot.login(**args):
        update.message.reply_text('Erro ao efetuar seu login, por favor verifique as credenciais e tente novamente!')
        user_data.clear()
        return ConversationHandler.END

    return instaBot


def help(bot, update):
    # TODO show info of how to use
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def cancel(bot, update, user_data):
    # Stops the conversation
    user = update.message.from_user
    logger.info("Usuário %s cancelou a conversa.", user.first_name)
    update.message.reply_text('Bye!.',
                              reply_markup=ReplyKeyboardRemove())

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

    return ConversationHandler.END


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LIKEBY: [RegexHandler('^(sim|nao)$', likeby, pass_user_data=True)],
            USERNAME: [MessageHandler(Filters.text, username, pass_user_data=True)],
            PASSWORD: [MessageHandler(Filters.text, password, pass_user_data=True)],
            LIKEBYHASHTAGS: [MessageHandler(Filters.text, likebyhashtags, pass_user_data=True)],
            LIKEFEED: [MessageHandler(Filters.text, likefeed, pass_user_data=True)],
            LIKELASTMEDIALIKERS: [MessageHandler(Filters.text, likelastmedialikers, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
    )

    # on different commands - answer in Telegram
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
