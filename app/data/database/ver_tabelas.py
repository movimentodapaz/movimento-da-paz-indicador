import sqlite3

conn = sqlite3.connect("paz.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()

print("📦 Tabelas no banco:")
for t in tabelas:
    print("-", t[0])

conn.close()
