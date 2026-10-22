import sqlite3

def get_user(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = '" + username + "'")
    row = cur.fetchone()
    return {"id": row[0], "name": row[1], "email": row[2]}

def average_age(users):
    return sum(u["age"] for u in users) / len(users)
