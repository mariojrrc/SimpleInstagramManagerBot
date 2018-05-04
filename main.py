from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
import configparser
import os

# Enable logging
from ExtendedBot import ExtendedBot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# get token from '.ini' file
config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')

USERNAME, PASSWORD, LIKEBY, LIKEBYHASHTAGS, LIKEBYUSERNAMES = range(5)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Bem vindo ao SimpleIntagramManager Bot! \n'
                              'Preciso de suas credenciais, qual nome de usuário?')

    return USERNAME


def username(bot, update, user_data):
    user = update.message.from_user
    user_data['username'] = update.message.text
    logger.info("username informado pelo %s é: %s", user.first_name, update.message.text)
    update.message.reply_text('Obrigado, agora preciso de sua senha de login.')

    return PASSWORD


def password(bot, update, user_data):
    reply_keyboard = [['hashtags', 'usernames']]
    user_data['password'] = update.message.text
    user = update.message.from_user
    logger.info("Senha informada pelo %s é: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Thanks! Gostaria de curtir por hashtags ou por usernames?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return LIKEBY


def likeby(bot, update, user_data):
    user = update.message.from_user
    logger.info("Curtir por: %s", update.message.text)

    if update.message.text == 'hashtags':
        update.message.reply_text('Pod crer! Informe as hashtags sem \'#\' e separada por espaços.',
                                  reply_markup=ReplyKeyboardRemove())
        return LIKEBYHASHTAGS
    elif update.message.text == 'usernames':
        update.message.reply_text('Pod crer! Informe os nomes de usuários sem \'@\' e separada por espaços.',
                                  reply_markup=ReplyKeyboardRemove())
        return LIKEBYUSERNAMES
    else:
        update.message.reply_text('Não entendi, por favor repita.', reply_markup=ReplyKeyboardRemove())
        return LIKEBY


def likebyhashtags(bot, update, user_data):
    user = update.message.from_user
    logger.info("Hashtags são: %s", update.message.text)
    update.message.reply_text('Ok, efetuando login e início de curtidas automáticas.')

    bot = ExtendedBot()
    tags = update.message.text.split(' ')
    tasks_list = []
    for item in tags:
        logger.info("adicionado task para #%s", item)
        tasks_list.append((bot.like_hashtag, {'hashtag': item, 'amount': 2}))

    args = {'username': user_data['username'], 'password': user_data['password']}
    if not bot.login(**args):
        update.message.reply_text('Erro ao efetuar seu login, por favor verifique as credenciais e tente novamente!')
        user_data.clear()
        return ConversationHandler.END

    for func, arg in tasks_list:
        hashtag = arg['hashtag']
        amount = arg['amount']
        try:
            total = bot.get_total_hashtag_medias(hashtag, amount)
            update.message.reply_text("Curtindo {} foto(s) com a hashtag #{}.".format(len(total), hashtag))
            func(**arg)
            update.message.reply_text("Finalizado curtida de fotos com hashtag #{}.".format(hashtag))

        except Exception as e:
            logger.info(e.message)
            update.message.reply_text('Erro ao curtir a hashtag %s!' % hashtag)
            user_data.clear()
            return ConversationHandler.END

    update.message.reply_text('Finalizado! %d fotos foram curtidas!' % bot.total['likes'])

    return ConversationHandler.END


def likebyusernames(bot, update):
    user = update.message.from_user
    logger.info("Usuarios são: %s", update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')
    return ConversationHandler.END


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def cancel(bot, update, user_data):
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
    updater = Updater(config.get('telegram', 'token'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LIKEBY: [RegexHandler('^(hashtags|usernames)$', likeby, pass_user_data=True)],
            USERNAME: [MessageHandler(Filters.text, username, pass_user_data=True)],
            PASSWORD: [MessageHandler(Filters.text, password, pass_user_data=True)],
            LIKEBYHASHTAGS: [MessageHandler(Filters.text, likebyhashtags, pass_user_data=True)],
            LIKEBYUSERNAMES: [MessageHandler(Filters.text, likebyusernames, pass_user_data=True)]
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
