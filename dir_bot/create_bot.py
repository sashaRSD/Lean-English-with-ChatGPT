from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser
config = configparser.ConfigParser()
config.read("dir_bot/config.ini")
storage = MemoryStorage()

bot = Bot(token=config["TOKEN"]["token_telegramEN_test"])
dp = Dispatcher(bot, storage=storage)
