# Metodologia — Indicador de Paz

## Objetivo
Medir o nível de paz de países combinando violência organizada, violência interpessoal, militarização e sinais de crise humanitária. Também inclui o Índice Vibracional de Paz (abordagem complementar, integrativa).

## Componentes
1. **Violência interpessoal** — taxa de homicídios por 100k (UNODC).
2. **Mortes por conflito** — battle-related deaths per 100k (UCDP).
3. **Eventos violentos** — frequência e severidade (ACLED).
4. **Violência contra mulheres** — denúncias/estimativas por 100k (WHO/UN).
5. **Deslocados / Refugiados** — per 100k (UNHCR).
6. **Gasto militar per capita** — SIPRI.

## Normalização
Min–max por indicador (0–1), onde 1 = pior (mais violência). Alternativa: z-score.

## Agregação
Peso padrão (ajustável pelo usuário):
- homicídios: 0.25
- battle deaths: 0.25
- eventos (ACLED): 0.20
- VAW: 0.15
- gasto militar: 0.10
- deslocados: 0.05

ViolenceScore V = soma ponderada (0–1).  
Indicador de Paz IP = 100 * (1 - V).

## Índice Vibracional de Paz (complemento)
Combina fatores socioemocionais e estruturais (paz positiva):
- governança, liberdade, corrupção (indices), bem-estar (ex: Gallup), e indicadores de violência.
Escala 0–1000 (métrica transformada para aproximar leituras vibracionais simbólicas).

## Validação
- Comparar com Global Peace Index (IEP), análise de sensibilidade por pesos, e testes regionais.