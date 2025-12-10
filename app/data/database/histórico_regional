CREATE TABLE IF NOT EXISTS historical_peace_regional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    region TEXT NOT NULL,

    -- Pilares de paz (0 a 100)
    pilar_paz_tensao REAL,              -- paz em períodos de tensão coletiva
    pilar_protecao_vida REAL,           -- proteção à vida cotidiana
    pilar_estabilidade_convivencia REAL,-- estabilidade da convivência social
    pilar_compromisso_desarmamento REAL,-- compromisso com reduzir foco em armas
    pilar_cuidado_vulneraveis REAL,     -- cuidado com vidas vulneráveis

    -- Índice final de Paz Viva histórica
    indice_paz_viva_historica REAL      -- 0 a 100
);
