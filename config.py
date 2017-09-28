import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# main
DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', 'on', '+', 'enable', 'yes',)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# heroku
APP_NAME = os.getenv('APP_NAME', 'dummy')
PORT = int(os.getenv('PORT', '5000'))
