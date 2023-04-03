from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton("/Войти_в_сделку")
b2 = KeyboardButton("/Создать_сделку")
b3 = KeyboardButton("/Стоимость_услуг")
b4 = KeyboardButton("/Баланс")
b5 = KeyboardButton("/Статистика_сделок")
b6 = KeyboardButton("/Помощь(FAQ)")
b7 = KeyboardButton("/Отправить_жалобу")

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b1).insert(b2).add(b3).insert(b4).add(b5).insert(b6).add(b7)