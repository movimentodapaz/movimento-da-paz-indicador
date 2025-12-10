import sqlite3

DB_PATH = "paz.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

dados = [
    # year, region, pilar_paz_tensao, pilar_protecao_vida, pilar_estabilidade_convivencia,
    # pilar_compromisso_desarmamento, pilar_cuidado_vulneraveis, indice_paz_viva_historica

    (1914, "Europa",   20, 30, 25, 15, 30, 24),
    (1915, "Europa",   15, 25, 20, 10, 20, 18),
    (1916, "Europa",   10, 18, 15,  8, 15, 14),
    (1917, "Europa",   12, 20, 18,  9, 18, 16),
    (1918, "Europa",   25, 35, 30, 20, 35, 29),

    (1914, "Américas", 60, 65, 70, 55, 60, 62),
    (1915, "Américas", 58, 63, 68, 54, 58, 60),
    (1916, "Américas", 55, 60, 65, 50, 55, 57),
    (1917, "Américas", 52, 58, 62, 48, 52, 54),
    (1918, "Américas", 60, 65, 68, 55, 60, 62),
]

cursor.executemany("""
INSERT INTO historical_peace_regional (
    year,
    region,
    pilar_paz_tensao,
    pilar_protecao_vida,
    pilar_estabilidade_convivencia,
    pilar_compromisso_desarmamento,
    pilar_cuidado_vulneraveis,
    indice_paz_viva_historica
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", dados)

conn.commit()
conn.close()

print("✅ Dados históricos iniciais inseridos com sucesso.")
