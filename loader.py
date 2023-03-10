import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from config import Config
from misc.postcard_api import PostcardsClient
# from utils.db_api.db import Database
from utils.db_api.poscard_db import PostcardsDB
from utils.db_api.staff import Staff
from utils.db_api.usersdb import UsersDB
from utils.db_api.messages import Messages


# ChatBot objects
if Config.proxy_url:
    bot = Bot(token=Config.telegram_token, parse_mode=types.ParseMode.HTML, proxy=Config.proxy_url)
else:
    bot = Bot(token=Config.telegram_token, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
dp = Dispatcher(bot, storage=storage)

# Database objects
# db = Database()
# Users from database
users = UsersDB()
# Staff database
staff = Staff()
# Messages from database
messages = Messages()
# Postcards api client and db:
postcards = PostcardsClient()
postcards_db = PostcardsDB()

# Logging setup
logging.basicConfig(handlers=(logging.FileHandler('logs/log.txt'), logging.StreamHandler()),
                    format=u'%(asctime)s %(filename)s [LINE:%(lineno)d] #%(levelname)-15s %(message)s',
                    level=logging.INFO,
                    )
