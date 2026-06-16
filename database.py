import sqlite3

conn = sqlite3.connect("expenses.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    amount REAL
)
""")

title = "Food"
amount = 250

cursor.execute(
    "INSERT INTO expenses(title, amount) VALUES(?, ?)",
    (title, amount)
)

conn.commit()

cursor.execute("SELECT * FROM expenses")

data = cursor.fetchall()

print(data)

conn.close()