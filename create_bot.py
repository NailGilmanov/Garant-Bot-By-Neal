import config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

# proxy_url = 'http://proxy.server:3128'
# bot = Bot(token=config.TOKEN, proxy=proxy_url)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)
