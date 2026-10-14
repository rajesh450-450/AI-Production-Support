import sqlite3

connection = sqlite3.connect("conversation.db")

cursor = connection.cursor()

cursor.execute(
    "SELECT id, role, content FROM messages"
)

rows = cursor.fetchall()

print("\nMessages stored in SQLite\n")

for row in rows:
    print(row)

connection.close()