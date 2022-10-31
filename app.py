import sqlite3
from sqlite3 import OperationalError
from hashlib import blake2b
from datetime import datetime
import qrcode
import base64
from io import BytesIO

from flask import Flask, render_template

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


def generate_qrcode(url: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # To Base64
    buff = BytesIO()
    img.save(buff, format="JPEG")
    base64_bytes = base64.b64encode(buff.getvalue())
    base64_str = base64_bytes.decode('utf-8')
    return base64_str


@app.route('/')
def main():
    try:
        table_creation()
    except OperationalError:
        print("log : table already exist")

    return render_template("home.html")


if __name__ == '__main__':
    app.run()
    