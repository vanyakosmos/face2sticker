import enum
import logging

from time import sleep

import io
from telegram import Bot, Update, ChatAction, Message, ParseMode
from telegram.ext import Filters

from stickerizer import make_sticker

from .decorators import command_setup, config, log


logger = logging.getLogger(__name__)


class Stage(enum.Enum):
    WAIT_TITLE = enum.auto()
    WAIT_NAME = enum.auto()
    WAIT_PHOTOS = enum.auto()


def clear(update: Update, user_data: dict):
    if user_data.get('stage', None) is not None:
        msg = 'Clearing...'
        update.message.reply_text(msg)
        user_data.clear()


@command_setup(name='start')
@log
def start(bot: Bot, update: Update):
    del bot
    msg = ('This bot can create sticker pack from your selfies.\n'
           'Type /create to create new pack or /edit to edit existing one.\n'
           'Existing pack must be created by me and owned by you.')
    update.message.reply_text(msg)


@command_setup(name='create', pass_user_data=True)
@log
def create_pack(bot: Bot, update: Update, user_data: dict):
    del bot
    clear(update, user_data)

    if user_data.get('stage', None) is None:
        msg = 'How pack should be titled?'
        user_data['stage'] = Stage.WAIT_TITLE
        update.message.reply_text(msg)


@command_setup(name='edit', pass_user_data=True)
@log
def edit_pack(bot: Bot, update: Update, user_data: dict):
    del bot
    clear(update, user_data)

    user_data['stage'] = Stage.WAIT_NAME
    user_data['edit'] = True
    msg = ('Send name of your existing sticker pack.\n'
           'Remember, you can edit only your pack.')
    update.message.reply_text(msg)


@config(filters=Filters.text, pass_user_data=True)
@log
def text_handler(bot: Bot, update: Update, user_data: dict):
    stage = user_data.get('stage', None)

    if stage == Stage.WAIT_TITLE:
        get_title(bot, update, user_data)

    elif stage == Stage.WAIT_NAME:
        get_name(bot, update, user_data)


@config(filters=Filters.text, pass_user_data=True)
@log
def get_title(bot: Bot, update: Update, user_data: dict):
    del bot
    if user_data.get('stage', None) != Stage.WAIT_TITLE:
        logger.debug("Didn't expected title.")
        return

    user_data['stage'] = Stage.WAIT_NAME
    title = update.message.text
    user_data['title'] = title
    msg = (f'Pack title: "{title}".\n'
           f'Now provide short name for sticker pack. '
           f'It must be unique for telegram and will be used in pack url.')
    update.message.reply_text(msg)


@config(filters=Filters.text, pass_user_data=True)
@log
def get_name(bot: Bot, update: Update, user_data: dict):
    if user_data.get('stage', None) != Stage.WAIT_NAME:
        logger.debug("Didn't expected name.")
        return

    name = update.message.text.strip() + '_by_' + bot.username

    if user_data.get('edit', False):
        user_data['stage'] = Stage.WAIT_PHOTOS
        msg = f'Pack name: "{name}". Now send photos.'

    else:
        pack_created = bot.create_new_sticker_set(
            user_id=update.message.from_user.id,
            name=name,
            title=user_data.get('title',
                                'Some default not empty name for sticker pack'),
            png_sticker=open('media/blank.png', 'rb'),
            emojis='🌚'
        )

        if pack_created:
            user_data['stage'] = Stage.WAIT_PHOTOS
            msg = (f'Successfully created pack with name: "{name}".\n '
                   f'Now send photos.')
        else:
            msg = ('Such name ("{}") already exists or it is not appropriate.\n'
                   'Try again...')

    user_data['name'] = name
    update.message.reply_text(msg)


@config(filters=Filters.photo, pass_user_data=True)  # todo: add `| Filters.document`
@log
def get_photo(bot: Bot, update: Update, user_data: dict):
    del bot
    if user_data.get('stage', None) != Stage.WAIT_PHOTOS:
        logger.debug("It's not time for photos...")
        return

    if user_data.get('photos', None) is None:
        user_data['photos'] = []

    message = update.message

    # todo: limit number of photos
    # todo: accept documents
    if message.photo is None:
        update.message.reply_text('Waiting for photo...')
        return

    photo = message.photo[-1]
    user_data['photos'].append(photo.file_id)

    photo_num = len(user_data['photos'])
    msg = f'So far got {photo_num} photo(s).\n'
    if photo_num == 1:
        msg += 'Type /finish to finish.'

    update.message.reply_text(msg)


def status_update(bot: Bot, update: Update, message: Message or None, cur_photo, photos_n):
    if cur_photo >= photos_n and message:
        message.delete()
        return None

    cur_photo = str(cur_photo).rjust(len(str(photos_n)))
    msg = f'`Processing status: [ {cur_photo} / {photos_n} ]`'

    if message is None:
        message = update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    else:
        message = message.edit_text(msg, parse_mode=ParseMode.MARKDOWN)
    bot.send_chat_action(chat_id=update.effective_chat.id,
                         action=ChatAction.TYPING)
    return message


def add_stickers(bot: Bot, update: Update,
                 user_id, pack_name,
                 photos_ids, status_msg):
    photos_n = len(photos_ids)
    for i, photo_id in enumerate(photos_ids):
        bytes_array = io.BytesIO()
        file = bot.get_file(photo_id)
        file.download(out=bytes_array)

        sticker, emoji = make_sticker(bytes_array)
        bot.add_sticker_to_set(user_id=user_id, name=pack_name,
                               png_sticker=sticker.getbuffer(),
                               emojis=emoji)
        sticker.close()
        bytes_array.close()
        # sleep(5)
        status_update(bot, update, message=status_msg,
                      cur_photo=i + 1, photos_n=photos_n)


@command_setup(name='finish', pass_user_data=True)
@log
def finish(bot: Bot, update: Update, user_data: dict):
    if user_data.get('stage', None) != Stage.WAIT_PHOTOS:
        logger.debug('Nothing to finish.')
        return

    status_msg = status_update(bot, update, message=None,
                               cur_photo=0, photos_n=len(user_data['photos']))

    add_stickers(bot, update,
                 user_id=update.message.from_user.id,
                 pack_name=user_data['name'],
                 photos_ids=user_data['photos'],
                 status_msg=status_msg)
    # todo: remove blank.png

    name = user_data['name']
    sticker = bot.get_sticker_set(name).stickers[0]
    update.message.reply_text('Enjoy!')
    update.message.reply_sticker(sticker)
    user_data.clear()


command_handlers = [
    start,
    create_pack,
    edit_pack,
    finish,
]

message_handlers = [
    text_handler,
    get_photo,
]
