import sqlite3
from sqlite3 import OperationalError
from hashlib import blake2b
from datetime import datetime

from flask import Flask

app = Flask(__name__)


def table_creation():
    con = sqlite3.connect('database.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute('''CREATE TABLE hash(hash text primary key, url text, at datetime)''')
    con.commit()


def data_insertion(url: str, hashed_url: str) -> bool:
    con = sqlite3.connect('database.db', check_same_thread=False)
    cur = con.cursor()
    query = "SELECT COUNT(*) FROM hash WHERE hash = '" + hashed_url + "'"
    cur.execute(query)

    if cur.fetchall()[0][0] > 0:
        return False

    now = datetime.now()
    query = "INSERT INTO hash('hash', 'url', 'at') VALUES('" + hashed_url + "', '" + url + "', '" + str(now) + "')"
    cur.execute(query)
    con.commit()

    return True


def hash_url(url: str) -> str:
    hashed = blake2b(digest_size=4)
    hashed.update(format_url(url).encode())
    return hashed.hexdigest()


def format_url(url: str) -> str:
    return url.replace("www", "")


@app.route('/')
def main():
    try:
        table_creation()
    except OperationalError:
        print("log : table already exist")

    return "ok"


if __name__ == '__main__':
    app.run()
