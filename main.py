from flask import Flask, request, g
import sqlite3
import os
import json

app = Flask(__name__)
cwd = os.path.dirname(__file__)
DB = 'bookshop.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(os.path.join(cwd, DB))
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# def db_keys(table):
#     cur = get_db().cursor()
#     info = cur.execute(f'''PRAGMA table_info({table})''')
#     return [col[1] for col in info]

def to_json(items, one=False):
    if one:
        return dict(items)
    return {'data': [dict(item) for item in items]}

@app.route('/')
def index():
    return '<h1>API information</h1>'


@app.route('/all')
def all():
    cur = get_db().cursor()
    query = '''SELECT * FROM books'''
    try:
        order = request.args.get('order') or 'ASC'
        rows = cur.execute(
            f'''{query} ORDER BY {request.args['sort']} {order};''').fetchall()
    except:
        rows = cur.execute(f'''{query};''').fetchall()
    return to_json(rows)


@app.route('/book/<book_id>', methods=['GET', 'DELETE', 'PUT'])
def book_by_id(book_id):
    cur = get_db().cursor()
    try:
        book = next(cur.execute(f'''SELECT * FROM books WHERE id={book_id};'''))
    except:
        return 'Book not found.'

    if request.method == 'DELETE':
        cur.execute(f'''DELETE FROM books WHERE id={book_id};''')

    if request.method == 'PUT':
        params = dict(request.form)
        set = ','.join(f'{key}={value!r}' for key, value in params.items())
        # blow if not params
        try:
            cur.execute(f'''UPDATE books SET {set} WHERE id={book_id};''')
        except:
            return 'Invalid params!'

    if request.method == 'GET':
        return to_json(book, one=True)

    get_db().commit()
    method = 'Updated' if request.method == 'PUT' else 'Deleted'

    return f'Book successfully {method}'

@app.route('/new', methods=['POST'])
def new():
    cur = get_db().cursor()
    params = dict(request.form)
    try:
        cur.execute('''
            INSERT INTO books (title, author, genre, stock) VALUES (?, ?, ?, ?);''',
            (
                params.get('title'),
                params.get('author'),
                params.get('genre'),
                params.get('stock')
                # params.get('title', 'NULL'),
                # params.get('author', 'NULL'),
                # params.get('genre', 'NULL'),
                # params.get('stock', 'NULL')
            )
        )
        get_db().commit()
        return 'Book successfully Created'
    except:
        return 'Fail!'



if __name__ == '__main__':
    app.run(debug=True)
