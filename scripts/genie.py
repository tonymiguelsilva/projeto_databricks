#!/usr/bin/env python3
"""Pergunta e avalia o Genie Farol · Diretoria pela CLI Databricks."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path


def cli() -> str:
    if encontrado := shutil.which("databricks"):
        return encontrado
    base = os.environ.get("LOCALAPPDATA")
    candidatos = sorted((Path(base or "") / "Microsoft/WinGet/Packages").glob("Databricks.DatabricksCLI_*/databricks.exe"), reverse=True)
    if candidatos:
        return str(candidatos[0])
    raise RuntimeError("Databricks CLI não encontrado")


def api(metodo: str, caminho: str, profile: str, corpo: dict | None = None) -> dict:
    comando = [cli(), "api", metodo, caminho, "--profile", profile]
    if corpo is not None:
        comando += ["--json", json.dumps(corpo, ensure_ascii=False)]
    for tentativa in range(4):
        resultado = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if resultado.returncode == 0:
            return json.loads(resultado.stdout or "{}")
        erro = resultado.stderr.strip() or resultado.stdout.strip()
        if not any(codigo in erro for codigo in ("429", "502", "503", "timeout", "RESOURCE_EXHAUSTED", "TEMPORARILY", "EOF")):
            break
        time.sleep(5 * (tentativa + 1))
    raise RuntimeError(erro)


def achar(titulo: str, profile: str) -> str:
    token = None
    while True:
        caminho = "/api/2.0/genie/spaces?page_size=100" + (f"&page_token={token}" if token else "")
        resposta = api("get", caminho, profile)
        for espaco in resposta.get("spaces", []):
            if espaco.get("title") == titulo:
                return espaco["space_id"]
        token = resposta.get("next_page_token")
        if not token:
            raise RuntimeError(f"espaço não encontrado: {titulo}")


def perguntar(space_id: str, pergunta: str, profile: str) -> dict:
    inicio = api("post", f"/api/2.0/genie/spaces/{space_id}/start-conversation", profile, {"content": pergunta})
    conversa, mensagem = inicio["conversation_id"], inicio["message_id"]
    for _ in range(120):
        resposta = api("get", f"/api/2.0/genie/spaces/{space_id}/conversations/{conversa}/messages/{mensagem}", profile)
        if resposta.get("status") in ("COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"):
            break
        time.sleep(3)
    saida = {"status": resposta.get("status"), "texto": "", "sql": "", "linhas": []}
    for anexo in resposta.get("attachments", []) or []:
        if anexo.get("text"):
            saida["texto"] += anexo["text"].get("content", "")
        if anexo.get("query"):
            saida["sql"] = anexo["query"].get("query", "")
            resultado = api("get", f"/api/2.0/genie/spaces/{space_id}/conversations/{conversa}/messages/{mensagem}/attachments/{anexo['attachment_id']}/query-result", profile)
            saida["linhas"] = resultado.get("statement_response", {}).get("result", {}).get("data_array") or []
    return saida


def executar_sql(sql: str, profile: str, warehouse: str) -> list[list]:
    resposta = api("post", "/api/2.0/sql/statements", profile, {"warehouse_id": warehouse, "statement": sql, "wait_timeout": "50s"})
    while resposta["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        resposta = api("get", f"/api/2.0/sql/statements/{resposta['statement_id']}", profile)
    if resposta["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(resposta["status"].get("error", {}).get("message", "SQL falhou"))
    return resposta.get("result", {}).get("data_array") or []


def normalizar(valor: object) -> str:
    try:
        return f"{round(float(valor), 2):g}"
    except (TypeError, ValueError):
        return str(valor or "").strip().lower()


def equivalente(genie: list[list], referencia: list[list]) -> bool:
    if not genie or len(genie) != len(referencia):
        return False
    restantes = [set(map(normalizar, linha)) for linha in genie]
    for linha in referencia:
        esperado = set(map(normalizar, linha))
        indice = next((i for i, obtido in enumerate(restantes) if esperado <= obtido), None)
        if indice is None:
            return False
        restantes.pop(indice)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("acao", choices=["perguntar", "benchmark"])
    parser.add_argument("titulo")
    parser.add_argument("argumento")
    parser.add_argument("--profile", default="DEFAULT")
    parser.add_argument("--warehouse", default="a25e41e310648f85")
    args = parser.parse_args()
    space_id = achar(args.titulo, args.profile)
    if args.acao == "perguntar":
        resposta = perguntar(space_id, args.argumento, args.profile)
        print(json.dumps(resposta, ensure_ascii=False, indent=2))
        return 0 if resposta["status"] == "COMPLETED" else 1
    casos = json.loads(Path(args.argumento).read_text(encoding="utf-8"))
    acertos = 0
    for numero, caso in enumerate(casos, 1):
        try:
            resposta = perguntar(space_id, caso["pergunta"], args.profile)
            esperado = executar_sql(caso["sql_referencia"], args.profile, args.warehouse)
            ok = resposta["status"] == "COMPLETED" and equivalente(resposta["linhas"], esperado)
        except RuntimeError as erro:
            resposta, ok = {"sql": str(erro)}, False
        acertos += int(ok)
        print(f"[{'ok' if ok else 'ERRO'}] {numero:02d}. {caso['pergunta']}")
        if not ok:
            print("      " + resposta.get("sql", "sem SQL")[:500].replace("\n", " "))
    print(f"\n{acertos}/{len(casos)} certas")
    return 0 if acertos >= 0.8 * len(casos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
