# Projeto Databricks

Repositório para desenvolvimento e versionamento de recursos do Databricks.

## Pré-requisitos

- Git
- Databricks CLI
- Acesso a um workspace Databricks

## Autenticação

```powershell
databricks auth login --host https://SEU-WORKSPACE.cloud.databricks.com
```

Depois, confirme a conexão:

```powershell
databricks current-user me
```

## Databricks Bundle

O alvo padrão `dev` usa o workspace configurado em `databricks.yml`.

```powershell
databricks bundle validate --profile DEFAULT
databricks bundle deploy --profile DEFAULT
```
