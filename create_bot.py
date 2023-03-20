import config
from aiogram import Bot, Dispatcher

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
