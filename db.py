import os
import sqlite3
import json

DB = 'bookshop.db'
json_db = 'bookshop.json'
cwd = os.path.dirname(__file__)
DBpath = os.path.join(cwd, DB)


def setup_data():
    conn = sqlite3.connect(DBpath)
    try:
        conn.cursor().execute('DROP TABLE books;')
    except:
        pass

    make_database(conn)
    populate(conn)

    conn.close()


def make_database(conn):
    conn.execute('''
        CREATE TABLE books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT(40) NOT NULL,
            author TEXT(20) NOT NULL,
            genre TEXT(20) NOT NULL,
            stock INTEGER NOT NULL
    );''')

def populate(conn):
    cur = conn.cursor()
    books = (
        (
            book['title'],
            book['author'],
            book['genre'],
            book['stock']
        )
        for book in data_json()
    )
    cur.executemany(
        '''INSERT INTO books (title, author, genre, stock) VALUES (?, ?, ?, ?);''',
        books
    )
    conn.commit()


def data_json():
    with open(os.path.join(cwd, json_db)) as f:
        return json.load(f)['data']


if __name__ == '__main__':
    setup_data()