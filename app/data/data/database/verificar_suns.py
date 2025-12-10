import sqlite3
from pathlib import Path

DB_PATH = Path("paz.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT id, country_code, city, latitude, longitude, created_at
FROM peacekeepers
ORDER BY id DESC
""")

dados = cursor.fetchall()
conn.close()

print("☀️ Sóis registrados:")
for linha in dados:
    print(linha)
