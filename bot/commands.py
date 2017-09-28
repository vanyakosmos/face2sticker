import enum

from time import sleep

from telegram import Bot, Update, ParseMode, ChatAction
from telegram.ext import Filters

from .decorators import command_setup, config


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
def start(bot: Bot, update: Update):
    del bot
    msg = ('This bot can create sticker pack from your selfies.\n'
           'Type "/create" to create new pack or "/edit" to edit existing one.')
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@command_setup(name='create', pass_user_data=True)
def create_pack(bot: Bot, update: Update, user_data: dict):
    del bot
    clear(update, user_data)

    if user_data.get('stage', None) is None:
        msg = 'How pack should be titled?'
        user_data['stage'] = Stage.WAIT_TITLE
        update.message.reply_text(msg)


@command_setup(name='edit', pass_user_data=True)
def edit_pack(bot: Bot, update: Update, user_data: dict):
    del bot
    clear(update, user_data)

    user_data['stage'] = Stage.WAIT_NAME
    user_data['edit'] = True
    msg = ('Send name of your existing sticker pack.\n'
           'Remember, you can edit only your pack.')
    update.message.reply_text(msg)


@config(filters=Filters.text, pass_user_date=True)
def get_title(bot: Bot, update: Update, user_data: dict):
    del bot
    if user_data.get('stage', None) != Stage.WAIT_TITLE:
        return

    user_data['stage'] = Stage.WAIT_NAME
    title = update.message.text
    user_data['title'] = title
    msg = (f'Using "{title}" as title for pack.\n'
           f'Now provide short name for sticker pack. It must be unique for telegram and will be used in pack url.')
    update.message.reply_text(msg)


@config(filters=Filters.text, pass_user_date=True)
def get_name(bot: Bot, update: Update, user_data: dict):
    if user_data.get('stage', None) != Stage.WAIT_NAME:
        return

    name = update.message.text

    if user_data.get('edit', False):
        user_data['stage'] = Stage.WAIT_PHOTOS
        msg = 'Got name.'

    else:
        pack_created = bot.create_new_sticker_set(
            user_id=update.message.from_user.id,
            name=name,
            title=user_data.get('title',
                                'Some default not empty name for sticker pack. Enjoy you lazy piece of shit!'),
            png_sticker=open('media/blank.png', 'rb'),
            emojis='🌚'
        )
        if pack_created:
            user_data['stage'] = Stage.WAIT_PHOTOS
            msg = 'Successfully created pack. Now add send photos.'
        else:
            msg = ('Such name ("{}") already exists or it is not appropriate.\n'
                   'Try again...')

    user_data['name'] = name
    update.message.reply_text(msg)


@config(filters=Filters.photo, pass_user_date=True)
def get_photo(bot: Bot, update: Update, user_data: dict):
    del bot
    if user_data.get('stage', None) != Stage.WAIT_PHOTOS:
        return

    if user_data.get('photos', None) is None:
        user_data['photos'] = []

    message = update.message

    # todo: accept files
    if message.photo is None:
        update.message.reply_text('Waiting for photo...')
        return

    photo = message.photo[-1]
    user_data['photos'].append(photo.file_id)

    photo_num = len(user_data['photos'])
    msg = f'So far got {photo_num} photo(s).\n'
    if photo_num == 1:
        msg += 'Type "/finish" to finish.'

    update.message.reply_text(msg)


@command_setup(name='finish', pass_user_data=True)
def finish(bot: Bot, update: Update, user_data: dict):
    if user_data.get('stage', None) != Stage.WAIT_PHOTOS:
        return

    bot.send_chat_action(chat_id=update.effective_chat.id,
                         action=ChatAction.FIND_LOCATION)

    # todo: make stickers...
    # todo: remove blank.png
    sleep(5)

    name = user_data['name']
    sticker = bot.get_sticker_set(name).stickers[0]
    update.message.reply_text('Enjoy!')
    update.message.reply_sticker(sticker)


command_handlers = [
    start,
    create_pack,
    edit_pack,
    finish,
]

message_handlers = [
    get_title,
    get_name,
    get_photo,
]
