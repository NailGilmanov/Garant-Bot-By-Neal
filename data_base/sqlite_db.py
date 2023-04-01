from datetime import datetime
import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect("users.db")
    cur = base.cursor()
    if base:
        print('Users data base connected OK.')
    base.execute('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, usd TEXT, rub TEXT, usdt TEXT, ton TEXT, btc TEXT, eth TEXT, bnb TEXT, busd TEXT, usdc TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS deals(id TEXT PRIMARY KEY, description TEXT, val TEXT, price TEXT, cite TEXT, founder TEXT, buyer TEXT, login TEXT, password TEXT, datetime TEXT, isstartet TEXT)')
    base.commit()


async def sql_add_user_command(state):
    cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(state.values()))
    base.commit()


async def sql_add_deal_command(state, message, dt):
    id = message.from_user.id
    id_of_deal = str(id)[0:4] + str(dt)
    buyer = 0
    cur.execute(f'INSERT INTO deals VALUES ({id_of_deal}, ?, ?, ?, ?, {id}, {str(buyer)}, ?, ?, {str(dt)}, {"False"})', tuple(state.values()))
    base.commit()


async def sql_get_balance(message):
    for ret in cur.execute(f"SELECT * FROM users WHERE id == {message.from_user.id}").fetchall():
        await bot.send_message(message.from_user.id, f"Пользователь: \n{message.from_user.username} [{message.from_user.id}]\n\nБаланс:\nUSD: {ret[1]}\nRUB: {ret[2]}\nUSDT: {ret[3]}\nTON: {ret[4]}\nBTC: {ret[5]}\nETH: {ret[6]}\nBNB:{ret[7]}\nBUSD: {ret[8]}\nUSDC: {ret[9]}")


async def sql_get_deal(message, id):
    for ret in cur.execute(f'SELECT * FROM deals WHERE id == {id} AND isstartet == {str(0)}').fetchall():
        cur_state = ''
        if ret[10] == "0":
            cur_state = 'Сделка еще не начата'
        else:
            cur_state = "Сделка была начата"
        time = f'{ret[9][:2]}:{ret[9][2:4]} {ret[9][4:6]}.{ret[9][6:8]}.{ret[9][8:]}'
        await bot.send_message(message.from_user.id, f"Сделка [{id}]\nСоздатель: {ret[5]}\n\nОписание: {ret[1]}\nЦена: {ret[3]} {ret[2]}\nСайт: {ret[4]}\nВремя создание сделки: {time}\nСостояние сделки: {cur_state}")
        await message.reply("Войти в сделку?\nВведите ДА или НЕТ")


async def start_deal(message, id):
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

    ostatok = True

    cur.execute(f'UPDATE deals SET buyer = {message.from_user.id} WHERE id == {id}')

    for ret in cur.execute(f'SELECT * FROM deals WHERE id == {id}').fetchall():
        last_amount = ''
        for ret1 in cur.execute(f"SELECT {ret[2]} FROM users WHERE id == {ret[6]}").fetchall():
            last_amount = ret1[0]

        if float(last_amount) - float(ret[3]) >= 0:
            cur.execute(f'UPDATE users SET {ret[2]} = {str(float(last_amount) - float(ret[3]))} WHERE id == {ret[6]}')
        else:
            ostatok = False
            zero = '0'
            await message.reply("На вашем счете не достаточно средств.\n\nПополнить счет обратившись в техническую поддержку @AOS_quartz")
            cur.execute(f'UPDATE deals SET buyer = {zero} WHERE id == {id}')

    if ostatok:
        isstartet = '1'
        # print(message.from_user.username, id)
        cur.execute(f'UPDATE deals SET buyer = {message.from_user.id} WHERE id == {id}')
        cur.execute(f'UPDATE deals SET datetime = {dt} WHERE id == {id}')
        cur.execute(f'UPDATE deals SET isstartet = {isstartet} WHERE id == {id}')

        for ret in cur.execute(f'SELECT * FROM deals WHERE id == {id}').fetchall():
            last_amount = ''
            for ret1 in cur.execute(f"SELECT {ret[2]} FROM users WHERE id == {ret[5]}").fetchall():
                last_amount = ret1[0]
            cur.execute(f'UPDATE users SET {ret[2]} = {str(float(last_amount) + float(ret[3]))} WHERE id == {ret[5]}')
            await message.reply('Сделка была успешно начата!')
            await bot.send_message(message.from_user.id, f'Вы можете проверить аккаунт:\n\nЛогин: {ret[7]}\nПароль: {ret[8]}\n\nВ случае возникновения трудностей вы можете втечении 15 минут отправить жалобу и сделка будет рассмотрена администраторами')

        base.commit()


async def sql_get_user_balance(id, name):
    for ret in cur.execute(f"SELECT * FROM users WHERE id == {id}").fetchall():
        await bot.send_message(id, f"Пользователь: \n{name} [{id}]\n\nБаланс:\nUSD: {ret[1]}\nRUB: {ret[2]}\nUSDT: {ret[3]}\nTON: {ret[4]}\nBTC: {ret[5]}\nETH: {ret[6]}\nBNB:{ret[7]}\nBUSD: {ret[8]}\nUSDC: {ret[9]}")


async def sql_check_deals(message):
    first = True
    for ret in cur.execute(f'SELECT * FROM deals WHERE buyer = {str(message.from_user.id)}').fetchall():
        if first:
            first = False
            await bot.send_message(message.from_user.id, 'Сделки в роли покупателя:')
        time = f'{ret[9][:2]}:{ret[9][2:4]} {ret[9][4:6]}.{ret[9][6:8]}.{ret[9][8:]}'
        await bot.send_message(message.from_user.id, f"Сделка [{ret[0]}]\nСоздатель: {ret[5]}\n\nОписание: {ret[1]}\nЦена: {ret[3]} {ret[2]}\nСайт: {ret[4]}\nВремя создание сделки: {time}\nСостояние сделки: сделка завершена")


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
