from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

home = ReplyKeyboardMarkup(resize_keyboard=True).add('Добавить песню').insert('Рейтинг песен')

home_admin = ReplyKeyboardMarkup(resize_keyboard=True).add('Добавить песню').insert('Рейтинг песен').add('Переключить песню')