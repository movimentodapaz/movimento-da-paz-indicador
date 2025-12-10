import sqlite3
from pathlib import Path

# ajuste aqui se o seu paz.db estiver em outra pasta
DB_PATH = Path("paz.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE peacekeepers ADD COLUMN city TEXT;")
    conn.commit()
    print("✅ Coluna 'city' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    print("⚠️ Atenção:", e)

conn.close()
