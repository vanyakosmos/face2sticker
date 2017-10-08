import logging

from telegram import Bot, ParseMode, Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import logs
from config import APP_NAME, BOT_TOKEN, DEBUG, PORT
from .conversation import conversation_handler
from .decorators import log
from .utils import weighted_choice


logs.set_up(DEBUG)
logger = logging.getLogger(__name__)

TITLE, NAME, PHOTO = range(3)


def error(bot: Bot, update: Update, err):
    logger.exception(err)


@log
def start(bot: Bot, update: Update):
    update.message.reply_text(
        'This bot can create sticker pack from your selfies.\n'
        '\n'
        '/create - create new pack\n'
        '/cancel - cancel pack creation\n'
        '\n'
        'If you want to <b>edit or delete</b> pack then ask @Stickers for help.',
        parse_mode=ParseMode.HTML
    )


@log
def sticker_handler(bot: Bot, update: Update):
    messages = [
        ('Cool sticker.', 5),
        ('Nice one.', 5),
        ('Majestic.', 5),
        ('Marvellous.', 5),
        ("I don't remember creating this one.", 5),
        ("Actually I don't like stickers and they force me to create them... (help)", 1),
    ]
    msg = weighted_choice(messages)
    update.message.reply_text(msg)


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.sticker, sticker_handler))
    dp.add_handler(conversation_handler)
    dp.add_error_handler(error)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
        updater.bot.set_webhook(f"https://{APP_NAME}.herokuapp.com/{BOT_TOKEN}")
    updater.idle()


if __name__ == '__main__':
    main()
