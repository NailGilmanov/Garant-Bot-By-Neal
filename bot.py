import config
import logging

from aiogram import Bot, Dispatcher, executor, types

#log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# /start, /help
@dp.message_handler (commands=["start", "help"])
async def greeting(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Привет! Я гарант бот и могу помогать тебе безопасно проводить сделки. Читай информацию и можешь начинать работать со мной!"
    )

# /price
@dp.message_handler (commands=["price"])
async def greeting(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Расценки на услуги бота: \n Со сделок до 500₽ 10% \n От 500₽ до 1000₽ - 9% \n От 1000₽ до 5000₽ - 8% \n От 5000₽ до 10000₽ - 7% \n От 10000₽ и больше - 6%"
    )

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
