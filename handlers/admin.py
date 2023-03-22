from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from data_base import sqlite_db

IDS = [int(i) for i in open("admins.txt", 'r').readlines()]


class FSMAdmin(StatesGroup):
    id_of_deal = State()
    name = State()


class FSMAddSum(StatesGroup):
    id_of_user = State()
    val = State()
    amount = State()


class FSMRemoveSum(StatesGroup):
    id_of_user = State()
    val = State()
    amount = State()


# Получение ID модераторов
# @dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global IDS
    open("admins.txt", 'w').write(str(message.from_user.id))
    await message.reply(f"Админ добавлен \nТекущий список админов: {IDS}")


#@dp.message_handler(commands='Добавить_сумму', state=None)
async def add_sum_start(message: types.Message):
    if message.from_user.id in IDS:
        await FSMAddSum.id_of_user.set()
        await message.reply("Введи id пользователя")


async def get_id_to_add(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["id"] = message.text
        await FSMAddSum.next()
        await message.reply("Введи валюту \nНапример, usd, rub, usdt, ton, btc, eth, bnb, busd, usdc")


async def get_val_to_add(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["val"] = message.text
        await FSMAddSum.next()
        await message.reply("Введи сумму\nНапример, 100")


async def get_amount_to_add(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["amount"] = message.text

        try:
            await sqlite_db.add_to_balance(data["id"], data["val"], data["amount"])

            await message.reply(f"Баланс пользователя [{data['id']}] успешно пополнен\n\nПроверить его можно воспользовавшись командой /Узнать_информацию_о_пользователе")
        except ValueError:
            await message.reply("Были введены неверные данные\n\nПопытайтесь снова")

        await state.finish()

# remove money

async def remove_sum_start(message: types.Message):
    if message.from_user.id in IDS:
        await FSMRemoveSum.id_of_user.set()
        await message.reply("Введи id пользователя")


async def get_id_to_remove(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["id"] = message.text
        await FSMRemoveSum.next()
        await message.reply("Введи валюту \nНапример, usd, rub, usdt, ton, btc, eth, bnb, busd, usdc")


async def get_val_to_remove(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["val"] = message.text
        await FSMRemoveSum.next()
        await message.reply("Введи сумму\nНапример, 100")


async def get_amount_to_remove(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["amount"] = message.text

        try:
            await sqlite_db.remove_from_balance(data["id"], data["val"], data["amount"])

            await message.reply(f"Баланс пользователя [{data['id']}] успешно снят\n\nПроверить его можно воспользовавшись командой /Узнать_информацию_о_пользователе")
        except ValueError:
            await message.reply("Были введены неверные данные\n\nПопытайтесь снова")

        await state.finish()


# @dp.message_handler(commands="Узнать_информацию_о_сделке", state=None)
async def cm_start(message: types.Message):
    if message.from_user.id in IDS:
        await FSMAdmin.id_of_deal.set()
        await message.reply("Введи id пользователя")


async def get_id(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["id"] = message.text
        await FSMAdmin.next()
        await message.reply("Введи ник пользователя")


# @dp.message_handler(state=FSMAdmin.id_of_deal)
async def get_name(message: types.Message, state: FSMContext):
    if message.from_user.id in IDS:
        async with state.proxy() as data:
            data["name"] = message.text

        await sqlite_db.sql_get_user_balance(data["id"], data["name"])

        await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=["Узнать_информацию_о_пользователе"], state=None)
    dp.register_message_handler(get_id, state=FSMAdmin.id_of_deal)
    dp.register_message_handler(get_name, state=FSMAdmin.name)

    dp.register_message_handler(add_sum_start, commands=["Добавить_сумму"], state=None)
    dp.register_message_handler(get_id_to_add, state=FSMAddSum.id_of_user)
    dp.register_message_handler(get_val_to_add, state=FSMAddSum.val)
    dp.register_message_handler(get_amount_to_add, state=FSMAddSum.amount)

    dp.register_message_handler(remove_sum_start, commands=["Снять_деньги"], state=None)
    dp.register_message_handler(get_id_to_remove, state=FSMRemoveSum.id_of_user)
    dp.register_message_handler(get_val_to_remove, state=FSMRemoveSum.val)
    dp.register_message_handler(get_amount_to_remove, state=FSMRemoveSum.amount)

    dp.register_message_handler(make_changes_command, commands=['moderator'])
