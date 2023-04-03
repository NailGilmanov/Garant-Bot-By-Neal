from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot
from keys import kb_client
from data_base import sqlite_db
import sqlite3 as sq
from datetime import datetime


class FSMMakeAppeal(StatesGroup):
    id_of_deal = State()
    comment = State()


async def start_appeal(message: types.Message):
    await FSMMakeAppeal.id_of_deal.set()
    await message.reply('Введи ID сделки')


async def load_id_of_deal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ID'] = message.text
    await FSMMakeAppeal.next()
    await message.reply('Напишите ваш комментарий')


async def load_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
    await state.finish()


class FSMMakeDeal(StatesGroup):
    des = State()
    val = State()
    price = State()
    cite = State()
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
        data['Valute'] = message.text.lower()
    if data['Valute'] not in ["usd", "rub", "usdt", "ton", "btc", "eth", "bnb", "busd", "usdc"]:
        await message.reply('Выбрана неверная валюта.\n')
        await state.finish()
    else:
        await FSMMakeDeal.next()
        await message.reply("Введите цену\nНапример, 100")


async def set_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Price'] = message.text
    await FSMMakeDeal.next()
    await message.reply("Введите сайт продаваемого аккаунта\nНапример, gumtree.com.au")


async def set_cite(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Cite'] = message.text
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

    curr = datetime.now()

    hour = curr.hour
    minute = curr.minute
    day = curr.day
    month = curr.month

    if curr.hour <= 9: hour = f'0{curr.hour}'
    if curr.minute <= 9: minute = f'0{curr.minute}'
    if curr.day <= 9: day = f'0{curr.day}'
    if curr.month <= 9: month = f'0{curr.month}'

    dt = f'{hour}{minute}{day}{month}{curr.year}'

    async with state.proxy() as data:
        await message.reply(f'Сделка [{str(message.from_user.id)[0:4] + str(dt)}] успешно создана!\nПередайте покупателю ID сделки для завершения операции')

    await sqlite_db.sql_add_deal_command(data, message, dt)

    await state.finish()


class FSMEnterDeal(StatesGroup):
    id_of_deal = State()
    agree = State()


# @dp.message_handler(commands='Создать_сделку', state=None)
async def start_enter(message: types.Message):
    await FSMEnterDeal.id_of_deal.set()
    await message.reply("Отправь айди сделки")


async def set_id_of_deal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_end'] = False
        data['id_of_deal'] = message.text
    try:
        await sqlite_db.sql_get_deal(message, data['id_of_deal'])
        await FSMEnterDeal.next()
    except:
        await message.reply("Введен неверный ID сделки")
        await state.finish()


# @dp.message_handler(state=FSMMakeDeal.des)
async def set_agree(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['agree'] = message.text

    if data['is_end']:
        await state.finish()
    elif data['agree'].lower() == 'нет':
        await message.reply("Сделка была отменена")
    else:
        await sqlite_db.start_deal(message, data['id_of_deal'])

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
        "Инструкция как пользоваться ботом:\n1. Вы создаете заявку на покупку\n2. Вводите id человека с кем будет заключена сделка\n3. Вносите оплату\n4. Бот проверяет товар на валидность\n5. После обмена на рассмотрение жалоб уделяется 15 минут \n\nПосле этого бот и админы не несут ответственности за качество товара \n\nЕсли у вас остались вопросы пишите мне: @AOS_quartz"
    )


async def info_about_deals(message: types.Message):
    await sqlite_db.sql_check_deals(message)


def register_handlers_client(dp: Dispatcher):
    # создание услуги
    dp.register_message_handler(start_deal, commands=["Создать_сделку"], state=None)
    # Выход из состояния
    dp.register_message_handler(cancel_handler, state="*", commands="Отмена")

    dp.register_message_handler(set_des, state=FSMMakeDeal.des)
    dp.register_message_handler(set_val, state=FSMMakeDeal.val)
    dp.register_message_handler(set_price, state=FSMMakeDeal.price)
    dp.register_message_handler(set_cite, state=FSMMakeDeal.cite)
    dp.register_message_handler(set_login, state=FSMMakeDeal.login)
    dp.register_message_handler(set_password, state=FSMMakeDeal.password)

    # вход в услугу
    dp.register_message_handler(start_enter, commands=["Войти_в_сделку"], state=None)
    dp.register_message_handler(set_id_of_deal, state=FSMEnterDeal.id_of_deal)
    dp.register_message_handler(set_agree, state=FSMEnterDeal.agree)

    # вход в услугу
    dp.register_message_handler(start_appeal, commands=["Отправить_жалобу"], state=None)
    dp.register_message_handler(load_id_of_deal, state=FSMMakeAppeal.id_of_deal)
    dp.register_message_handler(load_comment, state=FSMMakeAppeal.comment)

    # прочее
    dp.register_message_handler(greeting, commands=["start"])
    dp.register_message_handler(price, commands=["Стоимость_услуг"])
    dp.register_message_handler(faq, commands=["Помощь(FAQ)"])
    dp.register_message_handler(info_about_deals, commands=["Статистика_сделок"])

    dp.register_message_handler(check_balance, commands=["Баланс"])
