CREATE OR REPLACE VIEW lakehouse_vertice.gold.mv_projetos
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: lakehouse_vertice.gold.projeto_situacao_atual
comment: Métricas governadas da carteira de projetos em andamento na fotografia de 16/10/2026
filter: status = 'em_andamento'
dimensions:
  - name: projeto_id
    expr: projeto_id
    display_name: Código do projeto
    comment: Identificador único no formato PRJ-000
    synonyms: [código, id do projeto]
  - name: projeto
    expr: projeto
    display_name: Projeto
    comment: Código e nome completo do projeto
    synonyms: [nome do projeto, iniciativa]
  - name: cliente
    expr: cliente
    display_name: Cliente
    comment: Cliente atendido pelo projeto
    synonyms: [conta, empresa cliente]
  - name: segmento
    expr: segmento
    display_name: Segmento
    comment: Segmento econômico do cliente
    synonyms: [setor, indústria]
  - name: ferramenta
    expr: ferramenta
    display_name: Ferramenta de gestão
    comment: Ferramenta usada para gerenciar o cronograma
    synonyms: [sistema de gestão, ferramenta do projeto]
  - name: situacao
    expr: situacao
    display_name: Situação
    comment: Classificação atual entre ok, atenção e crítico
    synonyms: [risco, saúde do projeto]
  - name: farol_do_gerente
    expr: farol_do_gerente
    display_name: Farol do gerente
    comment: Farol informado pelo gerente do projeto
    synonyms: [farol informado, status do gerente]
  - name: farol_calculado
    expr: farol_calculado
    display_name: Farol calculado
    comment: Farol calculado a partir do SPI
    synonyms: [farol automático, status calculado]
  - name: gerente_projeto
    expr: gerente_projeto
    display_name: Gerente do projeto
    comment: Pessoa responsável pela gestão do projeto
    synonyms: [gerente, responsável]
measures:
  - name: projetos
    expr: COUNT(1)
    display_name: Projetos em andamento
    comment: Quantidade de projetos em andamento
    synonyms: [quantidade de projetos, total de projetos]
  - name: carteira
    expr: SUM(valor_contrato)
    display_name: Valor da carteira
    comment: Soma do valor contratado dos projetos em andamento
    synonyms: [valor contratado, receita da carteira]
  - name: spi
    expr: SUM(ev) / SUM(pv)
    display_name: SPI da carteira
    comment: Índice de prazo calculado pela razão entre EV e PV agregados
    synonyms: [índice de prazo, desempenho de prazo]
  - name: cpi
    expr: SUM(ev) / SUM(ac)
    display_name: CPI da carteira
    comment: Índice de custo calculado pela razão entre EV e AC agregados
    synonyms: [índice de custo, desempenho de custo]
  - name: eac
    expr: SUM(eac)
    display_name: Custo estimado ao término
    comment: Soma do custo estimado ao término dos projetos
    synonyms: [estimativa ao término, custo final estimado]
  - name: estouro_previsto
    expr: SUM(estouro_previsto)
    display_name: Estouro previsto
    comment: Soma do custo estimado acima do orçamento
    synonyms: [estouro de orçamento, sobrecusto]
  - name: margem_projetada
    expr: (SUM(valor_contrato) - SUM(eac)) / SUM(valor_contrato)
    display_name: Margem projetada
    comment: Margem da carteira após o custo estimado ao término
    synonyms: [margem prevista, rentabilidade projetada]
  - name: atraso_projetado_medio_dias
    expr: AVG(atraso_projetado_dias)
    display_name: Atraso projetado médio
    comment: Média de dias de atraso projetado dos projetos em andamento
    synonyms: [atraso médio, dias de atraso]
  - name: projetos_em_risco
    expr: COUNT(1) FILTER (WHERE situacao IN ('atenção', 'crítico'))
    display_name: Projetos em risco
    comment: Projetos em situação de atenção ou crítica
    synonyms: [projetos atrasados, projetos preocupantes]
  - name: projetos_criticos
    expr: COUNT(1) FILTER (WHERE situacao = 'crítico')
    display_name: Projetos críticos
    comment: Projetos com SPI ou CPI abaixo de 0,8
    synonyms: [críticos, projetos vermelhos]
  - name: projetos_melancia
    expr: COUNT(1) FILTER (WHERE melancia)
    display_name: Projetos melancia
    comment: Projetos com farol verde informado e SPI abaixo de 0,9
    synonyms: [melancias, falso verde]
$$;
