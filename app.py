import sqlite3
from sqlite3 import OperationalError
from hashlib import blake2b

from flask import Flask

app = Flask(__name__)


def table_creation():
    con = sqlite3.connect('database.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute('''CREATE TABLE hash(hash text primary key, url text)''')
    con.commit()


def hash_url(url: str) -> str:
    hashed = blake2b(digest_size=4)
    hashed.update(url.encode())
    return hashed.hexdigest()


@app.route('/')
def main():
    try:
        table_creation()
    except OperationalError:
        print("log : table already exist")

    return hash_url("https://amazon.com")


if __name__ == '__main__':
    app.run()
