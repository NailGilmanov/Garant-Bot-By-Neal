import logging
from create_bot import dp
from aiogram import executor

from handlers import client, admin, other

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

#log level
logging.basicConfig(level=logging.INFO)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
