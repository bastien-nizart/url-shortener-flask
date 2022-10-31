import sqlite3
from sqlite3 import OperationalError
from hashlib import blake2b
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from flask_wtf import FlaskForm

from flask import Flask, render_template, redirect
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'mY-SeCRet-kEy'
BASE_URL = "http://localhost:5000/"


class URLForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])


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


def get_history(number_of_row: int) -> list:
    con = sqlite3.connect('database.db', check_same_thread=False)
    cur = con.cursor()
    query = "SELECT * FROM hash ORDER BY at DESC"
    cur.execute(query)

    new_list = []
    count = 0
    for row in cur.fetchall():
        if count < number_of_row:
            new_list.append(row)
            count += 1

    return new_list


def generate_qrcode(url: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(BASE_URL + url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # To Base64
    buff = BytesIO()
    img.save(buff, format="JPEG")
    base64_bytes = base64.b64encode(buff.getvalue())
    base64_str = base64_bytes.decode('utf-8')
    return "data:image/png;base64," + base64_str


@app.route('/')
def main():
    try:
        table_creation()
    except OperationalError:
        print("log : table already exist")

    form = URLForm()

    return render_template("home.html", form=form)


@app.route('/link', methods=['GET', 'POST'])
def new_link():
    form = URLForm()

    if not form.validate_on_submit():
        return redirect("/")

    url = format_url(form.url.data)
    hashed = hash_url(url)
    data_insertion(url, hashed)
    return render_template("link.html", url=url, hashed=hashed, base_url=BASE_URL, qrcode=generate_qrcode(hashed))


if __name__ == '__main__':
    app.run()
