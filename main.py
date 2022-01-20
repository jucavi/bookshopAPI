from flask import Flask, request, g
import sqlite3
from db import DBpath

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DBpath)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def to_json(items, one=False):
    if one:
        return dict(items)
    return {'data': [dict(item) for item in items]}


def get_all(table, **params):
    sort = params.get('sort', 'NULL')
    order = params.get('order', 'ASC')
    if order.upper() not in ['ASC', 'DESC']:
        order = 'ASC'

    query = f'SELECT * FROM {table} ORDER BY {sort} {order};'
    cur = save_execute(query, changes=False)
    return cur.fetchall()


def get_by_id(table, Id, fields=('*',)):
    cur = get_db().cursor()
    fields = ','.join(fields)
    cur.execute(f'SELECT {fields} FROM {table} WHERE id=:id;', {'id': Id})
    return cur.fetchone()


def save_execute(query, args={}, changes=True):
    cur = get_db().cursor()
    try:
        cur.execute(query, args)
    except Exception as e:
        print(e)
    get_db().commit()
    if not changes:
        return cur
    return cur.rowcount


def delete_by_id(table, Id):
    return delete_by(table, 'id', Id)


def delete_by(table, field, value):
    query = f'DELETE FROM {table} WHERE {field}=:value;'
    return save_execute(query, {'value': value})


def update_by_id(table, Id, **params):
    return update(table, 'id', Id, **params)


def update(table, field, value, **params):
    set = ','.join(f'{key}={value!r}' for key, value in params.items())
    query = f'UPDATE {table} SET {set} WHERE {field}=:value;'
    return save_execute(query, {'value': value})


def new(table, **params):
    query = f'INSERT INTO {table} (title, author, genre, stock) VALUES(?, ?, ?, ?);'
    args = (
        params.get('title', 'NULL'),
        params.get('author', 'NULL'),
        params.get('genre', 'NULL'),
        params.get('stock', 'NULL')
    )
    return save_execute(query, args)


@app.route('/')
def index():
    return '<h1>API information</h1>'


@app.route('/all')
def all():
    return to_json(get_all('books', **request.args))


@app.route('/book/<book_id>', methods=['GET', 'DELETE', 'PUT'])
def book_by_id(book_id):
    book = get_by_id('books', book_id)
    if not book:
        return 'Not book found!'

    if request.method == 'DELETE':
        changes = delete_by_id('books', book_id)

    if request.method == 'PUT':
        changes = update('books', 'id', book_id, **request.form)

    if request.method == 'GET':
        return to_json(book, one=True)

    action = 'Updated' if request.method == 'PUT' else 'Deleted'
    if changes > 0:
        return f'Book successfully {action}, {changes} row changes'
    else:
        return 'No changes made! Invalid params'


@app.route('/new', methods=['POST'])
def new_book():
    changes = new('books', **request.form)
    if changes:
        return f'Book successfully Created, {changes} row changes.'
    return 'Something went wrong!'


if __name__ == '__main__':
    app.run(debug=True)
