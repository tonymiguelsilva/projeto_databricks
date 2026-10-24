-- Pessoas com utilização abaixo de 20% nas últimas 12 semanas.
SELECT colaborador_id,
       nome,
       papel,
       senioridade,
       projeto_id AS projeto_origem,
       projeto AS projeto_origem_nome,
       ROUND(SUM(horas_apontadas) / SUM(horas_disponiveis), 3) AS utilizacao_media,
       ROUND(SUM(horas_ociosas) / COUNT(DISTINCT semana), 1) AS horas_paradas_semana,
       ROUND(SUM(custo_ocioso) / COUNT(DISTINCT semana), 2) AS custo_ocioso_semana,
       MAX(custo_hora) AS custo_hora
FROM lakehouse_vertice.gold.utilizacao_pessoa_semana
WHERE semana > DATE'2026-07-24'
GROUP BY colaborador_id, nome, papel, senioridade, projeto_id, projeto
HAVING SUM(horas_apontadas) / SUM(horas_disponiveis) < 0.2
ORDER BY utilizacao_media
