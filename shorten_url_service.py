from flask import Flask, request, redirect
from handle_exception import *
import datetime as dt
import re
import exrex
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_shortcodes_in_db(connection):
    rows = connection.execute(
        'Select shortcode from urls_data ').fetchall()
    shortcodes = [row["shortcode"] for row in rows ] if rows else []
    return shortcodes


def get_data_of_shortcode(connection, shortcode):
    data = connection.execute(
        'Select url, created, lastRedirect, redirectCount'
        ' from urls_data where shortcode = (?)', (shortcode,)).fetchone()
    return data


def insert_entry_in_db(connection, shortcode, url):
    connection.execute(
        'INSERT INTO urls_data (shortcode, url, created, lastRedirect, redirectCount) VALUES (?,?,?,?,?)',
        (shortcode, url, dt.datetime.utcnow().isoformat(), None, 0))



@app.errorhandler(InvalidUsage)
def handle_error(error):
    return error.generate_message()


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.json if request.content_type == 'application/json' else request.args
    if "url" not in data.keys():
        raise InvalidUsage("Url not present", status_code=400)

    connection = get_db_connection()
    shortcodes = get_shortcodes_in_db(connection)
    if "shortcode" in data.keys():
        shortcode = data["shortcode"]
        if not re.match(r"^[A-Za-z0-9_]+$", shortcode) or len(shortcode) != 6:
            raise InvalidUsage("The provided shortcode is invalid", status_code=412)
        elif shortcode in shortcodes:
            raise InvalidUsage("Shortcode already in use", status_code=409)

    else:
        generate = True
        while generate:
            shortcode = exrex.getone(r"([A-Za-z0-9_]){6}")
            if shortcode not in shortcodes:
                generate = False

    connection.execute('INSERT INTO urls_data (shortcode, url, created, lastRedirect, redirectCount) '
                       'VALUES (?,?,?,?,?)',
                       (shortcode, data["url"], dt.datetime.utcnow().isoformat(), None, 0))

    connection.commit()
    connection.close()

    response_message = {
        "shortcode": shortcode
    }

    return jsonify(response_message), 201


@app.route("/<string:shortcode>", methods=["GET"])
def get_shortcode(shortcode):
    connection = get_db_connection()
    shortcodes = get_shortcodes_in_db(connection)
    if shortcode not in shortcodes:
        raise InvalidUsage("Shortcode not found", status_code=404)

    data = get_data_of_shortcode(connection, shortcode)

    connection.execute('UPDATE urls_data SET lastRedirect = ?, redirectCount = ? WHERE shortcode = ?',
                       (dt.datetime.utcnow().isoformat(), data["redirectCount"] + 1, shortcode))

    connection.commit()
    connection.close()
    return redirect(data["url"])  # default is already 302


@app.route("/<string:shortcode>/stats", methods=["GET"])
def get_shortcode_stats(shortcode):
    connection = get_db_connection()
    shortcodes = get_shortcodes_in_db(connection)
    if shortcode not in shortcodes:
        raise InvalidUsage("Shortcode not found", status_code=404)

    data = get_data_of_shortcode(connection, shortcode)
    connection.commit()
    connection.close()

    response_message = {
        "created": data["created"],
        "lastRedirect": data["lastRedirect"],
        "redirectCount": data["redirectCount"]
    }

    return jsonify(response_message)  # default is 200


if __name__ == "__main__":
    app.run()
