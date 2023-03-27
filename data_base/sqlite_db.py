import sqlite3 as sq
from create_bot import bot
from datetime import datetime


def sql_start():
    global base, cur
    base = sq.connect("users.db")
    cur = base.cursor()
    if base:
        print('Users data base connected OK.')
    base.execute('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, usd TEXT, rub TEXT, usdt TEXT, ton TEXT, btc TEXT, eth TEXT, bnb TEXT, busd TEXT, usdc TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS deals(id TEXT PRIMARY KEY, description TEXT, val TEXT, price TEXT, founder TEXT, buyer TEXT, login TEXT, password TEXT, datetime TEXT)')
    # base.execute('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, usd TEXT, rub TEXT)')
    base.commit()


async def sql_add_user_command(state):
    cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(state.values()))
    base.commit()


async def sql_add_deal_command(state, message):
    curr = datetime.now()
    dt = f'{curr.hour}{curr.minute}{curr.day}{curr.month}{curr.year}'
    id = message.from_user.id
    id_of_deal = str(id) + str(dt)
    cur.execute(f'INSERT INTO deals VALUES ({id_of_deal}, ?, ?, ?, {id}, ?, ?, ?, {str(dt)})', tuple(state.values()))
    base.commit()


async def sql_get_balance(message):
    for ret in cur.execute(f"SELECT * FROM users WHERE id == {message.from_user.id}").fetchall():
        await bot.send_message(message.from_user.id, f"Пользователь: \n{message.from_user.username} [{message.from_user.id}]\n\nБаланс:\nUSD: {ret[1]}\nRUB: {ret[2]}\nUSDT: {ret[3]}\nTON: {ret[4]}\nBTC: {ret[5]}\nETH: {ret[6]}\nBNB:{ret[7]}\nBUSD: {ret[8]}\nUSDC: {ret[9]}")


async def sql_get_user_balance(id, name):
    for ret in cur.execute(f"SELECT * FROM users WHERE id == {id}").fetchall():
        await bot.send_message(id, f"Пользователь: \n{name} [{id}]\n\nБаланс:\nUSD: {ret[1]}\nRUB: {ret[2]}\nUSDT: {ret[3]}\nTON: {ret[4]}\nBTC: {ret[5]}\nETH: {ret[6]}\nBNB:{ret[7]}\nBUSD: {ret[8]}\nUSDC: {ret[9]}")


async def add_to_balance(id, val, amount):
    last_amount = ''
    for ret in cur.execute(f"SELECT {val} FROM users WHERE id == {id}").fetchall():
        last_amount = ret[0]
    cur.execute(f'UPDATE users SET {val} = {str(float(last_amount) + float(amount))} WHERE id == {id}')
    base.commit()


async def remove_from_balance(id, val, amount):
    last_amount = ''
    for ret in cur.execute(f"SELECT {val} FROM users WHERE id == {id}").fetchall():
        last_amount = ret[0]
    cur.execute(f'UPDATE users SET {val} = {str(float(last_amount) - float(amount))} WHERE id == {id}')
    base.commit()
