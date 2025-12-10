import sqlite3

# ⚠️ AJUSTE SE NECESSÁRIO O CAMINHO DO BANCO
DB_PATH = "paz.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS historical_peace_regional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    region TEXT NOT NULL,

    pilar_paz_tensao REAL,
    pilar_protecao_vida REAL,
    pilar_estabilidade_convivencia REAL,
    pilar_compromisso_desarmamento REAL,
    pilar_cuidado_vulneraveis REAL,

    indice_paz_viva_historica REAL
);
""")

conn.commit()
conn.close()

print("✅ Tabela historical_peace_regional criada com sucesso.")
