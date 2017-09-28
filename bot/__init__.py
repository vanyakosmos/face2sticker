import logging

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler

from config import DEBUG, BOT_TOKEN, PORT, APP_NAME
import logs
from .commands import command_handlers, message_handlers
from .image_handler import image_handler


logs.set_up(DEBUG)
logger = logging.getLogger(__name__)


def error(bot: Bot, update: Update, err):
    del bot
    logger.warning(f'Update:\b {update}\nCaused error:\n{err}')


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    for handler in command_handlers:
        dp.add_handler(CommandHandler(**handler.get_config()))

    for handler in message_handlers:
        dp.add_handler(MessageHandler(**handler.get_config()))

    # [dp.add_handler(c) for c in command_list]
    # dp.add_handler(MessageHandler(Filters.photo, image_handler, pass_user_data=True))
    dp.add_error_handler(error)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
        updater.bot.set_webhook(f"https://{APP_NAME}.herokuapp.com/{BOT_TOKEN}")
    updater.idle()


if __name__ == '__main__':
    main()
