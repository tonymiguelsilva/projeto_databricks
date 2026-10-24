# Projeto Farol · Vértice

Este projeto usa Declarative Automation Bundles para ingestão e arquitetura medalhão no Databricks.

## For AI Agents: Use Databricks AI Tools

**BEFORE any Databricks action, read the project-local `databricks-core` skill at
`.agents/skills/databricks-core/SKILL.md`.**

It sets you up to work with this project reliably: CLI authentication, profile
selection, data discovery, and the bundle deployment workflow. Without it,
results are often slower and less accurate.

The project keeps Codex-compatible Databricks skills under `.agents/skills` so they
can be versioned with the repository. To refresh them from Databricks AI Tools, use:

```powershell
databricks aitools install --path .agents/skills --experimental
```

If the CLI is not installed, see: https://docs.databricks.com/dev-tools/cli/install

---

## Project Instructions

- Use sempre `--profile DEFAULT` nos comandos Databricks.
- Leia também `databricks-dabs`, `databricks-jobs`, `databricks-pipelines` e
  `databricks-serverless` antes de alterar recursos correspondentes.
- Nunca versione `.databricks/bundle/dev/variable-overrides.json` nem imprima segredos.
- O catálogo do projeto é `lakehouse_vertice`.
- O target `dev` deve manter agendamentos pausados e não deve usar `mode: development`.
- Não inicie uma execução se `vertice_farol` já estiver ativo.
- Ao alterar a implementação, mantenha `llm/prompt_01.md` sincronizado.
- Para mudanças em `minha-torre/`, leia `databricks-apps` e
  `databricks-app-design`; preserve npm, o perfil `DEFAULT`, Analytics e Genie.
- Para `gold.mv_projetos` ou `Farol · Diretoria`, leia também
  `databricks-metric-views` e `databricks-genie-agents`. O score é opcional e
  nunca pode ser referenciado pelo Genie ou pelo app quando a tabela não existir.
