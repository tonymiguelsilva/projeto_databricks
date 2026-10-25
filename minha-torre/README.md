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

A tela **Projetos em risco** apresenta os indicadores e a fila de atuação, identificando divergências entre o farol informado e o calculado como **Falso verde**, sem emoji. A tela **Simulador** estima a realocação de pessoas com utilização inferior a 20% nas últimas 12 semanas; “disponível” significa baixa utilização média, não ausência de projeto. No dataset atual, Sabrina Vasconcelos e Karina Ferraz são as duas pessoas elegíveis. A tela **Perguntar** conecta o usuário ao Genie `Farol · Diretoria` e exibe as consultas geradas. A tabela opcional `gold.score_estouro_30d` é acessada pela rota `/api/score-estouro`; sua ausência não interrompe o app.

O formulário do simulador usa uma grade responsiva: o projeto de destino recebe
mais espaço em telas amplas e os campos são reorganizados em telas menores.
O favicon próprio representa o radar/farol do projeto.

## Implantação

Execute na pasta `minha-torre`:

```powershell
databricks bundle validate --strict --profile DEFAULT
databricks bundle deploy --profile DEFAULT
.\scripts\conceder-acesso.ps1 -Profile DEFAULT
databricks apps deploy --auto-approve --profile DEFAULT
databricks apps get minha-torre --profile DEFAULT
```

Em Bash, use `./scripts/conceder-acesso.sh DEFAULT`. O service principal recebe somente `USE CATALOG`, `USE SCHEMA` e `SELECT` em `gold` e `silver`. O Genie usa OAuth em nome do usuário e requer consentimento no primeiro acesso. O app não usa Lakebase, persistência nem credenciais no código.
