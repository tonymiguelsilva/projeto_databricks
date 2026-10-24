-- Fotografia executiva dos projetos em andamento em 16/10/2026.
SELECT COUNT(*) AS projetos_em_andamento,
       COUNT_IF(situacao IN ('crítico', 'atenção')) AS projetos_em_risco,
       COUNT_IF(situacao = 'crítico') AS projetos_criticos,
       COUNT_IF(melancia) AS projetos_melancia,
       SUM(estouro_previsto) AS estouro_previsto,
       SUM(valor_contrato) AS carteira
FROM lakehouse_vertice.gold.projeto_situacao_atual
WHERE status = 'em_andamento'
