# Prompt App — Projeto Farol em Databricks Apps

Use as skills `databricks-apps` e `databricks-app-design` e siga o `AGENTS.md`. Crie o bundle AppKit independente `minha-torre/`, com React, TypeScript, npm e somente os plugins Analytics e Server. Use o perfil `DEFAULT`, o catálogo `lakehouse_vertice` e o warehouse `a25e41e310648f85`.

O app é somente leitura, sem Lakebase ou persistência. Mantenha três telas em português: **Projetos em risco**, **Simulador de realocação** e **Perguntar**, integrada ao Genie `Farol · Diretoria`. As queries versionadas são `kpis`, `projetos_risco` e `pessoas_ociosas`. Converta valores do warehouse com `Number()`, formate moeda em reais e índices com duas casas.

A tabela `lakehouse_vertice.gold.score_estouro_30d` é opcional e nunca deve entrar em `config/queries`. Consulte-a por `GET /api/score-estouro`; quando não existir, retorne `{disponivel:false, linhas:[]}` e mostre `—` nos indicadores do modelo.

O simulador usa pessoas com utilização menor que 20% nas últimas 12 semanas e projetos em atenção/crítico. Explique na interface que disponibilidade significa baixa utilização média, mostre o projeto de origem e use a chave composta pessoa/projeto. Para SRE, priorize `falta_sre`. Calcule horas mensais e ociosidade evitada multiplicando a média semanal por quatro, dias recuperados como impacto de 90 dias ÷ 90 × 30, mobilização como onboarding editável (40h) × custo/hora e saldo como ociosidade evitada menos mobilização. O formulário deve ser responsivo, reservar mais largura para o projeto de destino e truncar seu valor sem sobrepor o onboarding.

Use identidade própria de farol/radar e não use emoji de melancia. Preserve a coluna `melancia`, mas apresente o conceito como **Falso verde** ou **Divergência de farol**.

Valide com:

```powershell
npm run typegen -- --wait
npm run typecheck
npm run lint
npm test
databricks apps validate --profile DEFAULT
databricks bundle validate --strict --profile DEFAULT
databricks bundle deploy --profile DEFAULT
.\scripts\conceder-acesso.ps1 -Profile DEFAULT
databricks apps deploy --auto-approve --profile DEFAULT
```

O bundle raiz deve excluir `minha-torre/**` do sync. Nunca versione `.env`, token ou credencial.
