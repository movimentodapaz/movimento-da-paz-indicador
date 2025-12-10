import sqlite3
from pathlib import Path

DB_PATH = Path("paz.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================
# TABELA: country_metadata
# ============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS country_metadata (
    country_code TEXT PRIMARY KEY,
    country_name TEXT NOT NULL,
    latitude REAL,
    longitude REAL
);
""")

# ============================
# TABELA: peacekeepers
# ============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS peacekeepers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT,
    city TEXT,
    latitude REAL,
    longitude REAL,
    created_at TEXT
);
""")

# ============================
# TABELA: country_metrics
# ============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS country_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT,
    year INTEGER,
    month INTEGER,
    indicator_value REAL
);
""")

conn.commit()
conn.close()

print("✅ Banco paz.db criado com todas as tabelas.")
