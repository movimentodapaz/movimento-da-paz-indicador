import sqlite3
from pathlib import Path

DB_PATH = Path("paz.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM country_metadata;")
quantidade = cursor.fetchone()[0]

conn.close()

print("🌍 Quantidade de países na tabela country_metadata:", quantidade)
