from aiogram import types, Dispatcher
from create_bot import bot
from keys import kb_client


# /start, /help
async def greeting(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Привет! Я гарант бот и могу помогать тебе безопасно проводить сделки. Читай информацию и можешь начинать работать со мной!",
        reply_markup=kb_client
    )


# /price
async def price(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Расценки на услуги бота: \n Со сделок до 500₽ 10% \n От 500₽ до 1000₽ - 9% \n От 1000₽ до 5000₽ - 8% \n От 5000₽ до 10000₽ - 7% \n От 10000₽ и больше - 6%"
    )


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(greeting, commands=["start", "help"])
    dp.register_message_handler(price, commands=["Стоимость_услуг"])