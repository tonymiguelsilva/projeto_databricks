# Prompt Agente — Métricas governadas, Genie e AppKit

Use as skills `databricks-core`, `databricks-metric-views`, `databricks-genie-agents`, `databricks-dabs`, `databricks-jobs`, `databricks-apps` e `databricks-app-design`. Siga o `AGENTS.md`, use o perfil `DEFAULT` e preserve a data de referência `2026-10-16`.

Crie `lakehouse_vertice.gold.mv_projetos` como Metric View YAML 1.1 sobre `gold.projeto_situacao_atual`, filtrada para projetos em andamento. Centralize nela projetos, carteira, SPI por `SUM(ev)/SUM(pv)`, CPI por `SUM(ev)/SUM(ac)`, EAC, estouro, margem projetada, atraso médio, projetos em risco, críticos e melancias. Inclua descrições, nomes de exibição e sinônimos em português. Não use ponto e vírgula dentro do YAML.

Adicione `metricas_governadas` ao fim do job `vertice_farol`, dependente de `testes_de_qualidade` e `status_com_ia`. Implante e execute essa tarefa antes de publicar o Genie.

Gere deterministicamente `resources/farol.geniespace.json` com `scripts/gerar_genie.py`. O Genie `Farol · Diretoria` deve usar a Metric View, as quatro tabelas gold analíticas e `silver.entregas_fornecedor`. A tabela opcional `gold.score_estouro_30d` só pode ser incluída quando existir. IDs devem ser hexadecimais, únicos, com 32 caracteres e ordenados. Valide todos os exemplos SQL antes do deploy.

Publique o espaço como o recurso DAB nativo `genie_farol`, usando o warehouse `a25e41e310648f85`. Rode a pergunta executiva e o benchmark em `tests/genie-benchmark-diretoria.json`; aceite no mínimo 16/20 e ajuste metadados/exemplos antes de ampliar instruções textuais.

Integre o espaço `01f1cff8027f18b189265b533b804bdd` ao app `minha-torre`: recurso com `CAN_RUN`, escopo OAuth `genie`, variável de ambiente via `valueFrom`, plugin `genie()` e tela Perguntar com `GenieChat`. Mostre identidade autenticada, informe execução em nome do usuário e mantenha o aviso para revisar o SQL gerado. Não coloque arquivos `*.geniespace.json` dentro do app.

Valide os bundles, o AppKit, publique o app e confirme seu estado `RUNNING`. Não execute novamente ingestão, medalhão ou classificação de status.
