import sqlite3
from models import create_tables
con = sqlite3.connect('music_game.db')

cursor = con.cursor()

create_tables(cursor, con)

def register_user(id, username):
    cursor.execute(f"INSERT OR IGNORE INTO users (id, nickname) VALUES (?, ?)", (id, username))
    con.commit()


def load_song(user_id, song_name):
    print('loading song')
    cursor.execute('INSERT OR REPLACE INTO SONGS (name, author_id) VALUES (?,?)', (song_name, user_id))
    con.commit()