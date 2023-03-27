from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot
from keys import kb_client
from data_base import sqlite_db
import sqlite3 as sq


class FSMMakeDeal(StatesGroup):
    des = State()
    val = State()
    price = State()
    id_of_buyer = State()
    login = State()
    password = State()


# @dp.message_handler(commands='Создать_сделку', state=None)
async def start_deal(message: types.Message):
    await FSMMakeDeal.des.set()
    await message.reply("Отправь описание товара")


# Выход из состояния
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Создание сделки было отменено.")


# @dp.message_handler(state=FSMMakeDeal.des)
async def set_des(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Description'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введи чем вы будете оплачивать? \nНапример, usd, rub, usdt, ton, btc, eth, bnb, busd, usdc")


async def set_val(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Valute'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введите цену\nНапример, 100")


async def set_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Price'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введите ID покупателя")


async def set_buyer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['BuyerID'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введите логин продаваемого аккаунта")


async def set_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Login'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введите пароль продаваемого аккаунта")


async def set_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Password'] = message.text

    async with state.proxy() as data:
        await message.reply(str(data))

    await sqlite_db.sql_add_deal_command(data, message)

    await state.finish()


class FSMEnterDeal(StatesGroup):
    id_of_deal = State()


# @dp.message_handler(commands='Создать_сделку', state=None)
async def start_enter(message: types.Message):
    await FSMEnterDeal.id_of_deal.set()
    await message.reply("Отправь айди сделки")


# @dp.message_handler(state=FSMMakeDeal.des)
async def set_id_of_deal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id_of_deal'] = message.text

    async with state.proxy() as data:
        await message.reply(str(data))
    await state.finish()


# /start, /help
async def greeting(message: types.Message):
    already_register = False
    state = {
        "id": str(message.from_user.id),
        "usd": "0",
        "rub": "0",
        "usdt": "0",
        "ton": "0",
        "btc": "0",
        "eth": "0",
        "bnb": "0",
        "busd": "0",
        "usdc": "0"
    }
    try:
        await sqlite_db.sql_add_user_command(state)
    except sq.IntegrityError:
        already_register = True
        await bot.send_message(
            message.from_user.id,
            "Вы уже зарегистрированы! \nМожете проверить свой баналс нажав на одну из соотвествующих кнопок",
            reply_markup=kb_client
        )

    if not already_register:
        await bot.send_message(
            message.from_user.id,
            "Привет! Я гарант бот и могу помогать тебе безопасно проводить сделки. Читай информацию и можешь начинать работать со мной!",
            reply_markup=kb_client
        )

async def check_balance(message: types.Message):
    await sqlite_db.sql_get_balance(message)

# /price
async def price(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Расценки на услуги бота: \n Со сделок до 500₽ 10% \n От 500₽ до 1000₽ - 9% \n От 1000₽ до 5000₽ - 8% \n От 5000₽ до 10000₽ - 7% \n От 10000₽ и больше - 6%"
    )


# /faq
async def faq(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Инструкция как пользоваться ботом: \n\nЕсли у вас остались вопросы пишите мне: @absoluteriki"
    )


def register_handlers_client(dp: Dispatcher):
    # создание услуги
    dp.register_message_handler(start_deal, commands=["Создать_сделку"], state=None)
    # Выход из состояния
    dp.register_message_handler(cancel_handler, state="*", commands="Отмена")

    dp.register_message_handler(set_des, state=FSMMakeDeal.des)
    dp.register_message_handler(set_val, state=FSMMakeDeal.val)
    dp.register_message_handler(set_price, state=FSMMakeDeal.price)
    dp.register_message_handler(set_buyer, state=FSMMakeDeal.id_of_buyer)
    dp.register_message_handler(set_login, state=FSMMakeDeal.login)
    dp.register_message_handler(set_password, state=FSMMakeDeal.password)

    # вход в услугу
    dp.register_message_handler(start_enter, commands=["Войти_в_сделку"], state=None)
    dp.register_message_handler(set_id_of_deal, state=FSMEnterDeal.id_of_deal)

    # прочее
    dp.register_message_handler(greeting, commands=["start"])
    dp.register_message_handler(price, commands=["Стоимость_услуг"])
    dp.register_message_handler(faq, commands=["Помощь(FAQ)"])

    dp.register_message_handler(check_balance, commands=["Баланс"])