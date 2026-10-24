# Projeto Farol · Vértice

Bundle Databricks para ingerir arquivos do Supabase Storage, conferir a camada
bronze e publicar sete tabelas silver em um pipeline Lakeflow declarativo.

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

O target `dev` mantém o agendamento de segunda-feira às 6h pausado. O job usa
serverless `STANDARD`, permite somente uma execução simultânea e contém:

1. `ingestao_feriados`
2. `ingestao_data_lake`
3. `conferencia_bronze`
4. `medalhao`

## Estrutura

- `resources/`: job e pipeline declarados pelo bundle.
- `src/ingestao/`: notebooks da BrasilAPI e do Supabase/S3.
- `src/conferencia/`: contrato de contagens da bronze.
- `src/silver/`: sete tabelas silver declarativas.
- `src/setup/`: criação idempotente da infraestrutura Unity Catalog.
- `llm/prompt_01.md`: prompt operacional adaptado para Codex.
