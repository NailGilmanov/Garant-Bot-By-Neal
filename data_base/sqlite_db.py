import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect("users.db")
    cur = base.cursor()
    if base:
        print('Users data base connected OK.')
    base.execute('CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, usd TEXT, rub TEXT, usdt TEXT, ton TEXT, btc TEXT, eth TEXT, bnb TEXT, busd TEXT, usdc TEXT)')
    base.commit()


async def sql_add_user_command(state):
    cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(state.values()))
    base.commit()
