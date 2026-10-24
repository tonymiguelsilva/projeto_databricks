-- gold.status_estruturado: transforma o status semanal em dados estruturados.
-- Regras resolvem casos determinísticos, AI Functions tratam os últimos 90 dias
-- e palavras-chave classificam o histórico. O MERGE evita repetir chamadas de IA.

CREATE TABLE IF NOT EXISTS lakehouse_vertice.gold.status_estruturado (
  projeto_id       STRING    COMMENT 'Identificador do projeto',
  data_status      DATE      COMMENT 'Sexta-feira de referência do status',
  farol            STRING    COMMENT 'Farol publicado pelo gerente: verde, amarelo ou vermelho',
  causa_bloqueio   STRING    COMMENT 'Causa estruturada do bloqueio ou ausência de bloqueio',
  bloqueio         STRING    COMMENT 'Resumo do que está travando o projeto, extraído por IA',
  quem_destrava    STRING    COMMENT 'Time, papel ou fornecedor que precisa agir, extraído por IA',
  dias_impacto     DOUBLE    COMMENT 'Impacto declarado no cronograma em dias; uma semana equivale a sete dias',
  metodo           STRING    COMMENT 'Método de classificação: regra, ia ou palavra_chave',
  texto_status     STRING    COMMENT 'Texto original do status semanal',
  _classificado_em TIMESTAMP COMMENT 'Momento em que a linha foi classificada'
)
COMMENT 'Status semanais estruturados incrementalmente por regras, AI Functions e palavras-chave';

MERGE INTO lakehouse_vertice.gold.status_estruturado AS alvo
USING (
  WITH novos AS (
    SELECT s.*, lower(coalesce(s.texto_status, '')) AS texto_normalizado
    FROM lakehouse_vertice.silver.status_semanal AS s
    LEFT ANTI JOIN lakehouse_vertice.gold.status_estruturado AS existente
      ON existente.projeto_id = s.projeto_id
     AND existente.data_status = s.data_status
  ),
  marcados AS (
    SELECT *,
           CASE
             WHEN status_vazio
               OR texto_normalizado RLIKE 'bloqueios: nenhum|sem bloqueios|nada relevante'
               THEN 'regra'
             WHEN data_status >= DATE'2026-07-18' THEN 'ia'
             ELSE 'palavra_chave'
           END AS metodo_classificacao
    FROM novos
  ),
  classificados_com_ia AS (
    SELECT
      projeto_id,
      data_status,
      ai_classify(
        texto_status,
        '["change_freeze","falta_sre","dependencia_fornecedor","rotatividade","mudanca_escopo","bug_retrabalho","aprovacao_cliente","sem_bloqueio"]',
        map('version', '2.0')
      ):response[0]::STRING AS causa_ia,
      ai_extract(
        texto_status,
        '{"bloqueio":{"type":"string","description":"o que está travando o projeto, em poucas palavras"},"quem_destrava":{"type":"string","description":"time, papel ou fornecedor que precisa agir para destravar"},"dias_impacto":{"type":"number","description":"impacto declarado em dias no cronograma; uma semana equivale a 7 dias"}}',
        map('version', '2.0')
      ) AS extracao_ia
    FROM marcados
    WHERE metodo_classificacao = 'ia'
  )
  SELECT
    m.projeto_id,
    m.data_status,
    m.farol,
    CASE
      WHEN m.status_vazio THEN 'nao_reportado'
      WHEN m.metodo_classificacao = 'regra' THEN 'sem_bloqueio'
      WHEN m.metodo_classificacao = 'ia' THEN i.causa_ia
      WHEN m.texto_normalizado RLIKE 'freeze|congelamento|janela de mudança|janela de deploy' THEN 'change_freeze'
      WHEN m.texto_normalizado RLIKE '\\bsre\\b|infraestrutura|ambiente de homologação' THEN 'falta_sre'
      WHEN m.texto_normalizado RLIKE 'forge|consultoria|fornecedor' THEN 'dependencia_fornecedor'
      WHEN m.texto_normalizado RLIKE 'saída de|rotatividade|onboarding' THEN 'rotatividade'
      WHEN m.texto_normalizado RLIKE 'escopo|change request|regra de negócio' THEN 'mudanca_escopo'
      WHEN m.texto_normalizado RLIKE 'bugs|regressão|refazendo' THEN 'bug_retrabalho'
      WHEN m.texto_normalizado RLIKE 'aprovação do cliente|homologação do cliente' THEN 'aprovacao_cliente'
      ELSE 'sem_bloqueio'
    END AS causa_bloqueio,
    i.extracao_ia:response:bloqueio::STRING AS bloqueio,
    i.extracao_ia:response:quem_destrava::STRING AS quem_destrava,
    coalesce(
      i.extracao_ia:response:dias_impacto::DOUBLE,
      CASE
        WHEN m.texto_normalizado RLIKE 'impacto estimado de [0-9]+ dias'
          THEN CAST(regexp_extract(m.texto_normalizado, 'impacto estimado de ([0-9]+) dias', 1) AS DOUBLE)
        WHEN m.texto_normalizado LIKE '%impacto estimado: 1 semana%' THEN 7.0
        WHEN m.texto_normalizado LIKE '%sem impacto%' THEN 0.0
      END
    ) AS dias_impacto,
    m.metodo_classificacao AS metodo,
    m.texto_status,
    current_timestamp() AS _classificado_em
  FROM marcados AS m
  LEFT JOIN classificados_com_ia AS i
    ON i.projeto_id = m.projeto_id
   AND i.data_status = m.data_status
) AS novo
ON alvo.projeto_id = novo.projeto_id
AND alvo.data_status = novo.data_status
WHEN NOT MATCHED THEN INSERT *;

SELECT metodo, causa_bloqueio, COUNT(*) AS quantidade_status
FROM lakehouse_vertice.gold.status_estruturado
GROUP BY metodo, causa_bloqueio
ORDER BY metodo, quantidade_status DESC;
