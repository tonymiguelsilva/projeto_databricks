# Minha Torre

Databricks App do Projeto Farol, construída com AppKit, React e TypeScript. O app é somente leitura e usa exclusivamente o plugin Analytics para consultar o SQL Warehouse `a25e41e310648f85`.

## Desenvolvimento

```powershell
npm install
npm run typegen -- --wait
npm run typecheck
npm run lint
npm test
```

A tela **Projetos em risco** apresenta os indicadores e a fila de atuação. A tela **Simulador** estima a realocação de pessoas com utilização inferior a 20%. A tabela opcional `gold.score_estouro_30d` é acessada pela rota `/api/score-estouro`; sua ausência não interrompe o app.

## Implantação

Execute na pasta `minha-torre`:

```powershell
databricks bundle validate --strict --profile DEFAULT
databricks bundle deploy --profile DEFAULT
.\scripts\conceder-acesso.ps1 -Profile DEFAULT
databricks apps deploy --auto-approve --profile DEFAULT
databricks apps get minha-torre --profile DEFAULT
```

Em Bash, use `./scripts/conceder-acesso.sh DEFAULT`. O service principal recebe somente `USE CATALOG`, `USE SCHEMA` e `SELECT` em `gold` e `silver`. O app não usa Lakebase, Genie, persistência nem credenciais no código.
