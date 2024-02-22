from aiogram import types
from check_user import admin
from config import DEV_USER_ID, LEADER_ID, TOKEN
from keyboards import home, home_admin
from db_interface import load_song, register_user
from sqlite3 import IntegrityError
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot
from db_interface import cursor, con
import json
from random import choice
import requests

class SongState(StatesGroup):
    awaiting_song_name = State()

class ChangeSongState(StatesGroup):
    awaiting_song_name = State()


async def print_id(message: types.Message):
    print(message.from_user.id)

async def get_user_ids():
    cursor.execute("SELECT id FROM USERS")
    rows = cursor.fetchall()
    user_ids = [row[0] for row in rows]
    return user_ids

async def send_message_to_user(bot_token, user_id, message_text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': user_id,
        'text': message_text
    }
    try:
        response = requests.post(url, params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print("Message sent successfully")
    except requests.RequestException as e:
        print(f"Error sending message: {e}")


async def make_vk_link(song):
    return f"<a href='https://vk.com/audio?q={song}'>{song}</a>"

async def make_yx_link(song):
    return f"<a href='https://music.yandex.ru/search/?text={song}'>{song}</a>"


async def start(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id
    welcome = 'Добро пожаловать в Cәй Party!'
    register_user(user_id, username)
    if admin(message):
        await message.reply(welcome, reply_markup=home_admin)
    else:
        await message.reply(welcome, reply_markup=home)

async def upload_track(message: types.Message):
    await message.reply('Присылайте песню')
    await SongState.awaiting_song_name.set()

async def get_song_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    load_song(user_id, message.text)
    await message.reply(f'Ваша песня - {message.text}!')
    await state.finish()

async def send_song_list_with_avg_mark(message: types.Message):
    # Fetch all songs and their average marks from the database
    cursor.execute('''
        SELECT S.name, AVG(M.mark) as avg_mark
        FROM SONGS S
        LEFT JOIN MARKS M ON S.id = M.song_id
        WHERE M.mark is not null
        GROUP BY S.id
        order by avg_mark desc
    ''')
    song_data = cursor.fetchall()

    # If there are no songs in the database, send a message indicating so
    if not song_data:
        await message.answer("Пока что нет оцененных песен")
        return

    # Prepare the message with the list of songs and their average marks
    response_message = "Рейтинг песен:\n\n"
    for song_name, avg_mark in song_data:
        response_message += f" - {await make_vk_link(song_name)}: {avg_mark}\n"

    # Send the message
    await message.answer(response_message, parse_mode='html')

async def send_song_keyboard(message: types.Message):
    # Fetch song names from the database
    cursor.execute('SELECT name FROM SONGS')
    songs = cursor.fetchall()

    # If there are no songs in the database, send a message indicating so
    if not songs:
        await message.answer("Еще нет добавленных песен")
        return

    # Create a keyboard with song names
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for song in songs:
        keyboard.add(song[0])  # Add each song name to the keyboard

    # Send the keyboard to the user
    await message.answer("Выбери песню:", reply_markup=keyboard)
    await ChangeSongState.awaiting_song_name.set()

async def change_current_song(message: types.Message, state: FSMContext):
    # Get the song name from the message
    if not admin(message):
        return

    song_name = message.text



    # Define the filename for the JSON file
    json_filename = 'current_song.json'

    # Open the JSON file in append mode
    with open(json_filename, 'w') as json_file:
        # Write the song name to the JSON file
        json.dump({"song_name": song_name}, json_file)
        json_file.write('\n')  # Add a newline character after each entry

    
    # Send a confirmation message
    response = f"Текущая песня - {song_name}"
    response += f"\n\n<a href='https://vk.com/audio?q={song_name}'>Найти в ВК</a>"
    response += f"\n\n<a href='https://music.yandex.ru/search?text={song_name}'>Найти в Яндекс Музыке</a>"


    await message.answer(response, parse_mode='html', reply_markup=home_admin)
    await state.finish()

    print('sending')
    for id in await get_user_ids():
        await send_message_to_user(TOKEN, id, 'Слушаем следующую песню!')


async def insert_or_replace_mark(message: types.Message):
    # Get the mark from the message
    try:
        mark = int(message.text)
        if mark < 0 or mark > 10:
            await message.reply("Оценка должна быть от 0 до 10")
            return
    except ValueError:
        await message.answer("Неккоретное сообщение, оценка должна быть от 0 до 10")
        return

    # Read the song name from the JSON file
    with open('current_song.json', 'r') as json_file:
        data = json.load(json_file)
        song_name = data.get("song_name")

    # Query the SONGS table to retrieve the corresponding song ID
    cursor.execute('SELECT id FROM SONGS WHERE name = ?', (song_name,))
    song_data = cursor.fetchone()
    if song_data is None:
        return
    song_id = song_data[0]

    # Insert or replace the mark in the MARKS table
    cursor.execute('INSERT OR REPLACE INTO MARKS (mark, song_id, author_id) VALUES (?, ?, ?)', (mark, song_id, message.from_user.id))
    con.commit()

    # Send a confirmation message
    emojis = ['💓','💕','💖','💝','💙','💜','🖤','💪','👌','✅','✔']
    await message.answer(choice(emojis))

def register_handlers(dp):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(print_id, commands=['id'])
    dp.register_message_handler(upload_track, text='Добавить песню')
    dp.register_message_handler(get_song_name, state=SongState.awaiting_song_name)
    dp.register_message_handler(send_song_list_with_avg_mark, text='Рейтинг песен')
    dp.register_message_handler(send_song_keyboard, text='Переключить песню')
    dp.register_message_handler(change_current_song, state=ChangeSongState.awaiting_song_name)
    dp.register_message_handler(insert_or_replace_mark)