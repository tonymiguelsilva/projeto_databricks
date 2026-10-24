# Declarative Automation Bundles Project

This project uses Declarative Automation Bundles (DABs) for deployment. Add project-specific instructions below.

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

<!-- Add your project-specific instructions, coding conventions, or notes here -->
