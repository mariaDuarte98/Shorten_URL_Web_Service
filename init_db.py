import sqlite3
from decouple import config

connection = sqlite3.connect('database.db')

with open(config("SCHEMA_PATH")) as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
