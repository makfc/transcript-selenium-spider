import glob
import threading
import os
import pickle
from telegram.ext import Updater, CommandHandler
import logging
import config

bot = None
logger = logging.getLogger(__name__)

LIST_CHAT_FILE_NAME = 'list_chat.pkl'
MESSAGE_TO_SEND = '出左成績\nhttps://swsdownload.vtc.edu.hk/swsdownload/'
list_chat = []
if os.path.exists(LIST_CHAT_FILE_NAME):
    list_chat = pickle.load(open(LIST_CHAT_FILE_NAME, "rb"))


def start(bot, update):
    if update.message.from_user.id == config.self_user_id:
        if update.message.chat in list_chat:
            update.message.reply_text('You have already subscribed before!')
        else:
            list_chat.append(update.message.chat)
            pickle.dump(list_chat, open(LIST_CHAT_FILE_NAME, "wb"))
            update.message.reply_text('Subscribe successful!')
    elif update.message.chat.type == 'private':
        update.message.reply_text('You user id (for self_user_id in config.py): {}'.format(update.message.from_user.id))


def unsub(bot, update):
    if update.message.from_user.id == config.self_user_id:
        if update.message.chat in list_chat:
            list_chat.remove(update.message.chat)
            pickle.dump(list_chat, open(LIST_CHAT_FILE_NAME, "wb"))
            update.message.reply_text('Unsubscribe successful!')
        else:
            update.message.reply_text('You have not subscribed!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def send_to_me(file_name):
    bot.send_message(config.self_user_id, MESSAGE_TO_SEND)
    bot.send_document(config.self_user_id, document=open(file_name, 'rb'))
    logger.info("send_to_me completed")


def send_to_all_groups():
    for chat in list_chat:
        # same as bot.send_message(chat_id, MESSAGE_TO_SEND)
        t = threading.Thread(target=bot.send_message,
                             args=(chat.id,
                                   MESSAGE_TO_SEND),
                             kwargs={})
        t.start()
        logger.info("send to chat_id: %s", chat.id)
    logger.info("send_to_all_groups completed")


def send_message(file_name):
    # same as send_to_me(file_name)
    t = threading.Thread(target=send_to_me,
                         args=(file_name,),
                         kwargs={})
    t.start()
    send_to_all_groups()


def send_message_async(file_name):
    t = threading.Thread(target=send_message, args=(file_name,), kwargs={})
    t.start()


def main():
    global bot

    """Run bot."""
    updater = Updater(token=config.telegram_bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    bot = dp.bot

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("unsub", unsub))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started")

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    # updater.idle()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
    send_message_async(glob.glob("*.pdf")[0])
    logger.info("All threads are started")
