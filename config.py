import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# main
DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', 'on', '+', 'enable', 'yes',)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# heroku
APP_HOST = os.getenv('APP_HOST', 'example.com')
PORT = int(os.getenv('PORT', '5000'))
