#!/usr/bin/env python3
"""Envia as credenciais do override local para o secret scope do Databricks."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OVERRIDE = ROOT / ".databricks/bundle/dev/variable-overrides.json"
SCOPE = "vertice"


def executar(args: list[str], profile: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["databricks", *args, "--profile", profile],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="DEFAULT")
    args = parser.parse_args()

    config = json.loads(OVERRIDE.read_text(encoding="utf-8"))
    segredos = {
        "s3-access-key-id": config["s3_access_key_id"],
        "s3-secret-access-key": config["s3_secret_access_key"],
    }
    if any(not valor or "PREENCHA" in valor for valor in segredos.values()):
        raise SystemExit("preencha o override local antes de sincronizar os segredos")

    criado = executar(["secrets", "create-scope", SCOPE], args.profile)
    if criado.returncode and "already exists" not in (criado.stderr + criado.stdout).lower():
        raise SystemExit(criado.stderr.strip() or criado.stdout.strip())

    for chave, valor in segredos.items():
        resultado = executar(
            ["secrets", "put-secret", SCOPE, chave, "--string-value", valor],
            args.profile,
        )
        if resultado.returncode:
            raise SystemExit(resultado.stderr.strip() or f"falha ao gravar {chave}")
        print(f"segredo sincronizado: {SCOPE}/{chave}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
