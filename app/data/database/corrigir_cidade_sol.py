import sqlite3
from pathlib import Path

DB_PATH = Path("paz.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Atualiza a cidade do primeiro Sol (id = 1)
cursor.execute("""
UPDATE peacekeepers
SET city = 'Rio de Janeiro'
WHERE id = 1
""")

conn.commit()
conn.close()

print("✅ Cidade corrigida com sucesso!")
