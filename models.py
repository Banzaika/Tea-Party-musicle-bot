def create_tables(cursor, con):
    cursor.execute('''CREATE TABLE IF NOT EXISTS USERS(
        id integer unique,
        nickname varchar(200)
    )''')
    con.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS SONGS(
        id integer PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        author_id integer,
        unique(author_id)
    )''')
    con.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS MARKS(
        mark integer,
        song_id integer,
        author_id integer,
        unique(author_id, song_id)
    )''')
    con.commit()
