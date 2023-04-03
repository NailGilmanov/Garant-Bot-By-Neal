import logging
from create_bot import dp
from aiogram import Bot, executor
from data_base import sqlite_db

from handlers import client, admin, other


async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

#log level
logging.basicConfig(level=logging.INFO)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
