import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE users (
    user_id integer unique,
    count_tickets integer default 0
)""")


cursor.execute("""CREATE TABLE tickets (
    user_id integer,
    ticket_number text,
    type1 text,
    type2 text,
    price integer
)""")