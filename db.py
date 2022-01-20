import sqlite3
import os
import json

cwd = os.path.dirname(__file__)

# con = sqlite3.connect(os.path.join(f'{cwd}/bookshop.db'))
# cur = con.cursor()

# with open(f'{cwd}/bookshop.json') as file:
#     data = json.load(file)['data']

# cur.execute('''DROP TABLE books;''')
# books = (tuple(book.values())[1:] for book in data)

# con.execute('''
#     CREATE TABLE books(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         title TEXT(40) NOT NULL,
#         author TEXT(20) NOT NULL,
#         genre TEXT(20) NOT NULL,
#         stock INTEGER NOT NULL
# );''')

# cur.executemany('''
#     INSERT INTO books (title, author, genre, stock)
#     VALUES (?, ?, ?, ?);''',
#     books
# )
# con.commit()
# con.close()

def books(rjson=True):
    try:
        with sqlite3.connect(os.path.join(f'{cwd}/bookshop.db')) as con:
            if rjson:
                con.row_factory = sqlite3.Row
            cur = con.cursor()
            rows = cur.execute('''SELECT * FROM books''')
            if not rjson:
                return rows.fetchall()
            return { 'data': [dict(book) for book in rows] }
    except Exception as e:
        print(e)
        