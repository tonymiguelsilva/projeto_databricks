# Projeto Farol · Vértice

Bundle Databricks para ingerir arquivos do Supabase Storage, conferir a camada
bronze e publicar sete tabelas silver e três tabelas gold em um pipeline
Lakeflow declarativo.

O bundle também publica o dashboard AI/BI **Projeto Farol · Portfólio**, com
visões executivas de portfólio, pessoas e fornecedores.

O diretório `minha-torre/` contém um bundle independente do Databricks App
**Projeto Farol**, com as telas Projetos em risco, Simulador de realocação e Perguntar.
Consulte [minha-torre/README.md](minha-torre/README.md) para validar e implantar.

## Pré-requisitos

- Databricks CLI autenticado no perfil `DEFAULT`.
- SQL Warehouse serverless `a25e41e310648f85`.
- Bucket no Supabase com as pastas esperadas: `pmo`, `rh`, `timesheet`,
  `financeiro`, `compras`, `excel`, `clickup` e `msproject`.

## Configurar o Supabase

O arquivo real de credenciais fica dentro de `.databricks/` e nunca entra no Git.
Crie-o a partir do exemplo:

```powershell
New-Item -ItemType Directory -Force .databricks/bundle/dev
Copy-Item config/variable-overrides.example.json .databricks/bundle/dev/variable-overrides.json
```

Edite `.databricks/bundle/dev/variable-overrides.json` e preencha:

- `s3_endpoint`
- `s3_regiao`
- `s3_bucket`
- `s3_access_key_id`
- `s3_secret_access_key`

Não cole essas credenciais em notebooks, YAML, issues ou mensagens.

Sincronize as duas chaves com o secret scope `vertice` antes do deploy:

```powershell
python scripts/sync_secrets.py --profile DEFAULT
```

O job recebe apenas referências `{{secrets/vertice/...}}`; os valores não ficam
armazenados nos parâmetros da tarefa.

As credenciais S3 atuais são somente leitura. O bucket contém 18 dos 20
cronogramas Excel do seed 42; os arquivos de `PRJ-020` e `PRJ-021`, reproduzidos
pelo gerador oficial, ficam em
`/Volumes/lakehouse_vertice/bronze/raw/_complementos/excel` e são incorporados
automaticamente pela ingestão.

## Criar a infraestrutura

```powershell
python scripts/run_sql.py src/setup/00-bootstrap.sql --profile DEFAULT --warehouse a25e41e310648f85
```

Esse comando cria o catálogo `lakehouse_vertice`, os schemas `bronze`, `silver`
e `gold`, e o volume `bronze.raw`.

## Validar, implantar e executar

```powershell
databricks bundle validate --strict --profile DEFAULT
databricks bundle deploy --profile DEFAULT
databricks bundle run vertice_farol --profile DEFAULT
```

Para gerar e implantar o dashboard como código:

```powershell
python scripts/gerar_dashboard.py
databricks bundle validate --strict --profile DEFAULT
databricks bundle deploy --profile DEFAULT
databricks bundle summary --profile DEFAULT
```

Dashboard implantado:

- [Rascunho](https://dbc-d9922c6a-e0c3.cloud.databricks.com/sql/dashboardsv3/01f1cff17f241a16bad0b83c33ef1e8f)
- [Publicado](https://dbc-d9922c6a-e0c3.cloud.databricks.com/dashboardsv3/01f1cff17f241a16bad0b83c33ef1e8f/published?w=1487041240090169)

O target `dev` mantém o agendamento de segunda-feira às 6h pausado. O job usa
serverless `STANDARD`, permite somente uma execução simultânea e contém:

1. `ingestao_feriados`
2. `ingestao_data_lake`
3. `conferencia_bronze`
4. `medalhao`
5. `testes_de_qualidade`
6. `status_com_ia`
7. `metricas_governadas`

A tarefa final publica `lakehouse_vertice.gold.mv_projetos`, fonte governada dos
KPIs usados pelo Genie [Farol · Diretoria](https://dbc-d9922c6a-e0c3.cloud.databricks.com/genie/rooms/01f1cff8027f18b189265b533b804bdd?w=1487041240090169).

Para regenerar e avaliar o agente:

```powershell
python scripts/gerar_genie.py --profile DEFAULT
databricks bundle deploy --profile DEFAULT
python scripts/genie.py benchmark "Farol · Diretoria" tests/genie-benchmark-diretoria.json --profile DEFAULT
```

Para recalcular silver/gold e executar em paralelo os testes e a classificação
incremental dos status, sem recarregar a bronze:

```powershell
databricks bundle run vertice_farol --only medalhao+ --profile DEFAULT
```

## Estrutura

- `resources/`: job e pipeline declarados pelo bundle.
- `scripts/gerar_dashboard.py`: gerador determinístico do dashboard AI/BI.
- `src/ingestao/`: notebooks da BrasilAPI e do Supabase/S3.
- `src/conferencia/`: contrato de contagens da bronze.
- `src/silver/`: sete tabelas silver declarativas.
- `src/gold/`: fotografia atual, evolução semanal e utilização de pessoas.
- `src/ia/`: classificação incremental do texto livre dos status.
- `src/metricas/`: Metric View com os KPIs governados do portfólio.
- `src/testes/`: dez contratos de qualidade executados depois do medalhão.
- `src/setup/`: criação idempotente da infraestrutura Unity Catalog.
- `llm/`: prompts operacionais adaptados para Codex.
- `minha-torre/`: AppKit React/TypeScript somente leitura com Analytics e Genie.
